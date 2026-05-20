from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('call', '0004_meeting_duration_participants'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='meeting',
            name='participant_names',
        ),
    ]
