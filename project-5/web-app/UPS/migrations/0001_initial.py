# Generated by Django 2.2 on 2019-04-19 02:06

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='package',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('worldid', models.CharField(default='', max_length=30, null=True)),
                ('status', models.CharField(choices=[('C', 'Created'), ('E', 'truck en route to warehouse'), ('W', 'truck waiting for package'), ('L', 'loaded and waiting for delivery'), ('O', 'out for delivery'), ('D', 'delivered')], max_length=30)),
                ('product_name', models.CharField(max_length=1000)),
                ('description', models.TextField()),
                ('count', models.IntegerField()),
                ('location_x', models.CharField(max_length=30, null=True)),
                ('location_y', models.CharField(max_length=30, null=True)),
                ('packageid', models.IntegerField()),
                ('truckid', models.CharField(default='', max_length=30, null=True)),
                ('name', models.CharField(max_length=1000)),
            ],
            options={
                'db_table': 'package',
            },
        ),
        migrations.CreateModel(
            name='truck',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('worldid', models.CharField(default='', max_length=30, null=True)),
                ('truckid', models.CharField(max_length=30)),
                ('packageid', models.CharField(default='0', max_length=10)),
                ('location_x', models.CharField(max_length=30, null=True)),
                ('location_y', models.CharField(max_length=30, null=True)),
                ('status', models.CharField(choices=[('I', 'idel'), ('E', 'truck en route to warehouse'), ('W', 'truck waiting for package'), ('L', 'loaded and waiting for delivery'), ('O', 'out for delivery')], max_length=30)),
            ],
            options={
                'db_table': 'truck',
            },
        ),
    ]
