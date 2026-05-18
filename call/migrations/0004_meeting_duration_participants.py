from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('call', '0003_remove_user_email_staff'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='ended_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='meeting',
            name='participant_names',
            field=models.TextField(blank=True, default=''),
        ),
    ]
