from django.db import migrations


def merge_libarian_into_member(apps, schema_editor):
    Member = apps.get_model("members", "Member")
    Libarian = apps.get_model("members", "Libarian")
    db_alias = schema_editor.connection.alias

    for libarian in Libarian.objects.using(db_alias).all().iterator():
        member = Member.objects.using(db_alias).filter(email=libarian.email).first()

        if member is None:
            member = Member(
                name=libarian.name,
                email=libarian.email,
                phone=libarian.phone,
                password=libarian.password,
                is_staff=True,
                is_superuser=libarian.is_superuser,
                is_active=libarian.is_active,
                date_joined=libarian.date_joined,
                last_login=libarian.last_login,
            )
            member.save(using=db_alias)
        else:
            changed_fields = []
            if not member.is_staff:
                member.is_staff = True
                changed_fields.append("is_staff")
            if libarian.is_superuser and not member.is_superuser:
                member.is_superuser = True
                changed_fields.append("is_superuser")
            if changed_fields:
                member.save(using=db_alias, update_fields=changed_fields)

        member.groups.add(*libarian.groups.using(db_alias).all())
        member.user_permissions.add(*libarian.user_permissions.using(db_alias).all())


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0002_alter_libarian_id_alter_member_id"),
    ]

    operations = [
        migrations.RunPython(merge_libarian_into_member, migrations.RunPython.noop),
        migrations.DeleteModel(
            name="Libarian",
        ),
        migrations.CreateModel(
            name="Librarian",
            fields=[],
            options={
                "verbose_name": "Librarian",
                "verbose_name_plural": "Librarians",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("members.member",),
        ),
    ]
