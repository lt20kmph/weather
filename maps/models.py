from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class Space(models.Model):
    lat = models.IntegerField(
            validators=[MinValueValidator(0),
                        MaxValueValidator(38)],
            )
    lon = models.IntegerField(
            validators=[MinValueValidator(0),
                        MaxValueValidator(51),]
            )
    class Meta:
        abstract = True

class SpaceHuman(Space):
    place = models.CharField(max_length=100)
    def __str__(self):
            return (self.place)

class SpaceTime(Space):
    # lat = models.IntegerField(
    #         validators=[MinValueValidator(0),
    #                     MaxValueValidator(38)],
    #         )
    # lon = models.IntegerField(
    #         validators=[MinValueValidator(0),
    #                     MaxValueValidator(51),]
    #         )
    year = models.IntegerField(
            validators=[MinValueValidator(1884),
                        MaxValueValidator(2018),]
            )

    class Meta:
        abstract = True

statChoices = [( 'tasmax' , 'Maximum Air Temp'),
               ( 'tasmin' , 'Minimum Air Temp'),
               ( 'sfcWind' , 'Surface Wind' ),
               ( 'rainfall' , 'Rainfall'),
               ( 'sun' , 'Hours of Sunshine')]

class MonthlyData(SpaceTime):
    stat = models.CharField(
            max_length=8,
            choices = statChoices,
            )
    month = models.IntegerField(
            validators=[MinValueValidator(0),
                        MaxValueValidator(11),]
            )
    data = models.FloatField()
    def __str__(self):
            return (self.stat,self.month,self.data)

class AnnualData(SpaceTime):
    stat = models.CharField(
            max_length=8,
            choices = statChoices,
            )
    data = models.FloatField()
    def __str__(self):
            return (self.stat,self.data)

class Explanations(models.Model):
    stat = models.CharField(
            max_length=8,
            choices = statChoices,
            )
    longname = models.CharField(
            max_length=100,
            )
    rangelower = models.IntegerField()
    label = models.CharField(
            max_length=20,
            )
    normalise = models.CharField(
            max_length=1,
            )
    exp = models.TextField()
    exp_mon = models.TextField()
    def __str__(self):
            return (self.stat,self.label)

class Xform(Space):
    xlat = models.FloatField()
    xlon = models.FloatField()
    def __str__(self):
            return (self.xlat,self.xlon)
