import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from Mktps.models import (
    Mktp,
    MktpSubCat,
    MktpSubCatField,
    MktpFieldMapping,
)

class Command(BaseCommand):
    help = ("Load MktpFieldMapping from an Amazon mktp mapping CSV.")

    errorsFile='./load_data_errors.txt'
    
    def add_arguments(self, parser):
        parser.add_argument("--csv",required=True,help="Path to the mapping CSV.",)
        parser.add_argument("--mktp",default="Amazon",help="Mktp name.",)
        parser.add_argument("--subcat",default="Bracelet",help="ArtHQ subcat name.",)
        parser.add_argument("--dry-run",action="store_true",help="Validate the CSV without changing the database.",)
        parser.add_argument("--replace",action="store_true",help=("Delete existing mappings for this mktp subcat and recreate them."),)

    def handle(self, *args, **options):
        csv_path = Path(options["csv"])
        if not csv_path.exists():
            raise CommandError(f"CSV file not found: {csv_path}")
        mktp_name = options["mktp"]
        subcat_name = options["subcat"]

        # =========================================================
        # 1. Get Mktp
        # =========================================================
        try:
            mktp = Mktp.objects.get(name=mktp_name)
        except Mktp.DoesNotExist:
            raise CommandError(f"Mktp '{mktp_name}' does not exist.")

        # =========================================================
        # 2. Get MktpSubCat
        # =========================================================
        try:
            mktp_subcat = (MktpSubCat.objects.select_related("mktp","subcat",)
                .get(mktp=mktp,subcat__name=subcat_name,))
        except MktpSubCat.DoesNotExist:
            raise CommandError("MktpSubCat not found: "f"{mktp_name} / {subcat_name}")

        # =========================================================
        # 3. Read CSV
        # =========================================================
        with csv_path.open("r",encoding="cp1252",newline="",) as file:
            reader = csv.DictReader(file)
            required_columns = {"Excel Row","Amazon Field #","code","Field","Value Type","Value",}
            actual_columns = set(reader.fieldnames or [])
            missing_columns = required_columns - actual_columns
            if missing_columns:
                raise CommandError(f"CSV is missing required columns: {sorted(missing_columns)}")
            csv_rows = list(reader)

        # =========================================================
        # 4. Basic CSV validation
        # =========================================================
        if len(csv_rows) != 400:
            raise CommandError(f"Expected exactly 400 CSV rows, found {len(csv_rows)}.")
        valid_value_types = {choice[0]for choice in MktpFieldMapping.ValueType.choices}
        csv_by_field_number = {}
        errors=[]
        with open(self.errorsFile,'w') as f:
            f.write("Starting run")
        for row in csv_rows:
            # -----------------------------------------------------
            # Amazon Field #
            # -----------------------------------------------------
            try:
                field_number = int(row["Amazon Field #"].strip())
            except (TypeError, ValueError):
                errors.append(f"Invalid Amazon Field #: {row['Amazon Field #']}")
            if not 1 <= field_number <= 400:
                errors.append(f"Amazon Field # must be between 1 and 400: {field_number}")
            if field_number in csv_by_field_number:
                errors.append(f"Duplicate Amazon Field #: {field_number}")

            # -----------------------------------------------------
            # Code
            # -----------------------------------------------------
            code = row["code"].strip()
            if not code:
                errors.append(f"Amazon Field #{field_number} has empty code.")

            # -----------------------------------------------------
            # Field name
            # -----------------------------------------------------
            field_name = row["Field"].strip()
            if not field_name:
                errors.append(f"Amazon Field #{field_number} ""has empty Field name.")

            # -----------------------------------------------------
            # Value Type
            # -----------------------------------------------------
            value_type = row["Value Type"].strip().upper()

            if value_type not in valid_value_types:
                errors.append(f"Invalid Value Type '{value_type}'for Amazon Field #{field_number}.")
            # -----------------------------------------------------
            # Value
            # -----------------------------------------------------
            raw_value = row["Value"]
            value = (raw_value.strip() if raw_value is not None else "")
            # -----------------------------------------------------
            # BLANK validation
            # -----------------------------------------------------
            if value_type == "BLANK" and value:
                errors.append(f"Amazon Field #{field_number} is BLANK but contains value '{value}'.")
            # -----------------------------------------------------
            # AI validation
            #
            # CSV may contain "Ollama" as a marker.
            # It will NOT be stored in MktpFieldMapping.value.
            # -----------------------------------------------------
            if value_type == "AI":
                if value and value.lower() != "ollama":
                    errors.append(f"Amazon Field #{field_number} is AI but contains unexpected value '{value}'. Expected 'Ollama' or blank.")
                value = None
            # -----------------------------------------------------
            # BLANK -> NULL
            # -----------------------------------------------------
            elif value_type == "BLANK":
                value = None
            # -----------------------------------------------------
            # Other types
            # -----------------------------------------------------
            else:
                value = value or None
            csv_by_field_number[field_number] = {
                "code": code,
                "field_name": field_name,
                "value_type": value_type,
                "value": value,
            }

        if len(errors)>0:
            errorstring=''
            for e in errors:
                errorstring += (e+'\n')
            with open(self.errorsFile,'a') as f:
                f.writelines(errorstring)
            raise CommandError (f"Errors is CSV Validations \n{errorstring}")
        # =========================================================
        # 5. Get MktpSubCatField records
        # =========================================================
        msfs = list(
            MktpSubCatField.objects
            .select_related("mktp_field")
            .filter(
                mktp_subcat=mktp_subcat
            )
            .order_by("column_order")
        )

        if len(msfs) != 400:
            raise CommandError(
                "Expected exactly 400 "
                "MktpSubCatField records, "
                f"found {len(msfs)}."
            )

        # =========================================================
        # 6. Validate column order
        # =========================================================

        expected_numbers = set(range(1, 401))

        db_numbers = {
            msf.column_order
            for msf in msfs
        }

        missing_db_numbers = (
            expected_numbers - db_numbers
        )

        extra_db_numbers = (
            db_numbers - expected_numbers
        )

        if missing_db_numbers:
            raise CommandError(
                "Missing MktpSubCatField "
                f"column_order values: "
                f"{sorted(missing_db_numbers)}"
            )

        if extra_db_numbers:
            raise CommandError(
                "Unexpected MktpSubCatField "
                f"column_order values: "
                f"{sorted(extra_db_numbers)}"
            )

        # =========================================================
        # 7. Match CSV -> MktpSubCatField
        # =========================================================

        mappings = []
        errors=[]
        for msf in msfs:
            field_number = msf.column_order
            if field_number not in csv_by_field_number:
                errors.append(f"No CSV record for Amazon Field #{field_number}.")
            csv_data = csv_by_field_number[field_number]
            mktp_field = msf.mktp_field
            # -----------------------------------------------------
            # Validate MktpField.code
            # -----------------------------------------------------
            if mktp_field.code != csv_data["code"]:
                errors.append(
                    "\nMktpField code mismatch.\n"
                    f"Amazon Field #: {field_number}\n"
                    f"DB code:         {mktp_field.code}\n"
                    f"CSV code:        {csv_data['code']}\n"
                    f"DB field name:   {mktp_field.name}\n"
                    f"CSV field name:  {csv_data['field_name']}"
                )
            # -----------------------------------------------------
            # Prepare mapping
            # -----------------------------------------------------
        if len(errors)>0:
            errorstring=''
            for e in errors:
                errorstring += (e+'\n')
            with open(self.errorsFile,'a') as f:
                f.writelines(errorstring)
            raise CommandError (f"Errors is CSV Matching \n{errorstring}")
        
        for msf in msfs:
            csv_data = csv_by_field_number[msf.column_order]
            mappings.append(MktpFieldMapping(
                    mktp_subcat_field=msf,
                    value_type=csv_data["value_type"],
                    value=csv_data["value"],
                    transformation={},
                    is_active=True,
                )
            )
        # =========================================================
        # 8. Print validation summary
        # =========================================================
        type_counts = {}
        for mapping in mappings:
            value_type = mapping.value_type
            type_counts[value_type] = (type_counts.get(value_type, 0) + 1)
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("CSV / database validation successful."))
        self.stdout.write(f"Mktp:  {mktp.name}")
        self.stdout.write(f"SubCat:  {mktp_subcat.subcat.name}")
        self.stdout.write(f"Fields:       {len(msfs)}")
        self.stdout.write("")
        self.stdout.write("Value Type summary:")
        for value_type in sorted(type_counts):
            self.stdout.write(f"  {value_type:<12} {type_counts[value_type]}")
        # =========================================================
        # 9. Dry run
        # =========================================================
        if options["dry_run"]:
            self.stdout.write("")
            self.stdout.write(self.style.WARNING("DRY RUN: database was not modified."))
            return
        # =========================================================
        # 10. Database update
        # =========================================================
        with transaction.atomic():
            if options["replace"]:
                deleted_count, _ = (MktpFieldMapping.objects.filter(mktp_subcat_field__in=msfs).delete())
                self.stdout.write(f"Deleted {deleted_count} existing mappings.")
                MktpFieldMapping.objects.bulk_create(mappings,batch_size=500,)
                created_count = len(mappings)
                updated_count = 0
            else:
                existing = {mapping.mktp_subcat_field_id: mapping for mapping in (MktpFieldMapping.objects.filter(mktp_subcat_field__in=msfs))}
                to_create = []
                to_update = []
                for new_mapping in mappings:
                    msf_id = (new_mapping.mktp_subcat_field_id)
                    if msf_id in existing:
                        existing_mapping = existing[msf_id]
                        existing_mapping.value_type = (new_mapping.value_type)
                        existing_mapping.value = (new_mapping.value)
                        existing_mapping.transformation = {}
                        existing_mapping.is_active = True
                        to_update.append(existing_mapping)
                    else:
                        to_create.append(new_mapping)
                if to_create:
                    MktpFieldMapping.objects.bulk_create(to_create,batch_size=500,)
                if to_update:
                    MktpFieldMapping.objects.bulk_update(to_update,
                        [
                            "value_type",
                            "value",
                            "transformation",
                            "is_active",
                        ],
                        batch_size=500,
                    )
                created_count = len(to_create)
                updated_count = len(to_update)
        # =========================================================
        # 11. Final verification
        # =========================================================

        final_count = (MktpFieldMapping.objects.filter(mktp_subcat_field__in=msfs).count())
        if final_count != 400:
            raise CommandError("Database verification failed. "f"Expected 400 mappings, found {final_count}.")
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("MktpFieldMapping successfully updated."))
        self.stdout.write(f"Created: {created_count}")
        self.stdout.write(f"Updated: {updated_count}")
        self.stdout.write(f"Total:   {final_count}")