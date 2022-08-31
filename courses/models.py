from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from helpers.models import BaseModel, generate_unique_slug
from common.models import User

from .fields import OrderField
from django.template.loader import render_to_string
class Subject(BaseModel):
    title = models.CharField(max_length=255, unique=True, blank=True, null=True, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
    
    def save(self, *args, **kwargs):
        if hasattr(self, "slug") and hasattr(self, "title"):
            if not self.slug:
                self.slug = generate_unique_slug(self.__class__, self.title)

        super().save(*args, **kwargs)
    

class Course(BaseModel):
    title = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True)
    overview = models.TextField(blank=True, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='courses')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses_created')

    students = models.ManyToManyField(User, related_name='courses_joined', blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Course"
        verbose_name_plural = "Courses"
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if hasattr(self, "slug") and hasattr(self, "title"):
            if not self.slug:
                self.slug = generate_unique_slug(self.__class__, self.title)

        super().save(*args, **kwargs)

    


class Module(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    order = OrderField(blank=True, null=True, for_fields=['course'], db_index=True)
    
    def __str__(self):
        return f'{self.order}. {self.title}'

    class Meta:
        ordering = ['order']
        verbose_name = "Module"
        verbose_name_plural = "Modules"


class Content(models.Model):
    module = models.ForeignKey(Module,
                               related_name='contents',
                               on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE,
                                     limit_choices_to={'model__in':(
                                     'text',
                                     'video',
                                     'image',
                                     'file')})
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')

    order = OrderField(blank=True, null=True, for_fields=['module'])

    class Meta:
        ordering = ['order']
        verbose_name = "Content"
        verbose_name_plural = "Contents"



class ItemBase(BaseModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='%(class)s_created')
    title = models.CharField(max_length=255, blank=True, null=True)

    
    class Meta:
        abstract = True

    def __str__(self):
        return self.title
    
    def render(self):
        return render_to_string(f'courses/content/{self._meta.model_name}.html', {'item': self})
    


class Text(ItemBase):
    content = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.content


class File(ItemBase):
    file = models.FileField(upload_to='files')

    def __str__(self):
        return self.file.name


class Image(ItemBase):
    image = models.ImageField(upload_to='images')

    def __str__(self):
        return self.image.name


class Video(ItemBase):
    url = models.URLField()

    def __str__(self):
        return self.url

