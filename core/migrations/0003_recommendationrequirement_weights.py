from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_recommendationprofile_recommendationrequirement'),
    ]

    operations = [
        migrations.AddField(
            model_name='recommendationrequirement',
            name='weights',
            field=models.JSONField(default=dict),
        ),
    ]
