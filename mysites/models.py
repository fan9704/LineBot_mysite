from django.db import models, connection

# Create your models here.
class Restaurant(models.Model):
    name=models.CharField(max_length=20)
    phone_number=models.CharField(max_length=15)
    address=models.CharField(max_length=50,blank=True)
    def __unicode__(self):
        return self.name
    def __str__(self):
        return self.name
class SpicyFoodManager(models.Manager):
    def get_queryset(self):
        return super(SpicyFoodManager, self).get_queryset().filter(is_spicy=True)
    def cheap_food_num(self):
        return self.filter(price_lte=100).count()
    def get_120_food(self):
        cursor = connection.cursor()
        cursor.execute("""
            SELECT name 
            FROM restaurants_food 
            WHERE price=120
        """)
        return [result[0] for result in cursor.fetchall()]
class Food(models.Model):
    name=models.CharField(max_length=20)
    price=models.DecimalField(max_digits=3,decimal_places=0)
    comment=models.CharField(max_length=50,blank=True)
    is_spicy=models.BooleanField(default=False)
    restaurant=models.ForeignKey(Restaurant,on_delete=models.SET)
    objects=SpicyFoodManager()
    def __unicode__(self):
        return self.name
    def __str__(self):
        return   self.name
    class Meta:
        ordering=['restaurant']

class Comment(models.Model):
    content=models.CharField(max_length=255)
    visitor=models.CharField(max_length=255)
    email=models.EmailField(max_length=255)
    date_time=models.DateTimeField()
    restaurant=models.ForeignKey(Restaurant,on_delete=models.SET)
    def __unicode__(self):
        return self.name
    def __str__(self):
        return   str(self.restaurant)+"  的評論"
    class Meta:
        ordering=['date_time']
        permissions=(
            ("can_comment","Can_comment"),

        )

class LineAccount(models.Model):
    u_id=models.CharField(max_length=255,primary_key=True)
    user_displayname=models.CharField(max_length=255)

class language(models.Model):
    request=models.CharField(max_length=100,primary_key=True)
    response=models.CharField(max_length=100)

class investigate(models.Model):
    User = models.CharField(max_length=255,primary_key=True)
    date = models.DateTimeField()
    program = models.CharField(max_length=50)

class image(models.Model):
    request = models.CharField(max_length=100, primary_key=True)
    response = models.CharField(max_length=100)

class AlbumModel(models.Model):
    adate=models.DateTimeField(auto_now=True)
    alocation=models.CharField(max_length=200,blank=True,default='')
    atitle=models.CharField(max_length=100,null=False)
    adesc=models.TextField(blank=True,default='')
    def __str__(self):
        return self.atitle

class PhotoModel(models.Model):
    palbum=models.ForeignKey('AlbumModel',on_delete=models.CASCADE)
    psubject=models.CharField(max_length=100,null=False)
    pdate=models.DateTimeField(auto_now=True)
    purl=models.CharField(max_length=100,null=False)
    phit=models.IntegerField(default=0)
    def __str__(self):
        return self.psubject