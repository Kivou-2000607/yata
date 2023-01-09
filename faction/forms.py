# Copyright 2019 kivou.2000607@gmail.com
#
# This file is part of yata.
#
#     yata is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     any later version.
#
#     yata is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with yata. If not, see <https://www.gnu.org/licenses/>.


from django import forms
from django.core.exceptions import ValidationError

from faction.models import Faction


class PosterHeadForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["posterHeadImg"].required = True

    def clean_posterHeadImg(self):
        data = self.cleaned_data["posterHeadImg"]
        print(data)
        if data is not None:
            if data.size > 500 * 1024:
                print("error head")
                raise ValidationError("Image size > 500kb", code="invalid")
            return data

    class Meta:
        model = Faction
        fields = ("posterHeadImg",)


class PosterTailForm(forms.ModelForm):
    def clean_posterTailImg(self):
        data = self.cleaned_data["posterTailImg"]
        print(data)
        if data is not None:
            if data.size > 500 * 1024:
                print("error tail")
                raise ValidationError("Image size > 500kb", code="invalid")
            return data

    class Meta:
        model = Faction
        fields = ("posterTailImg",)


#
#
# def image_validator(upload):
#     max_size = 5000000
#     Error = False
#     ErrorMsg = []
#     acceptable_types = [ 'image/jpeg', 'image/png' ]
#     str_acceptable_types = ', '.join( [s.split('/')[-1].upper() for s in acceptable_types[:-1]] ) + ' ou ' + acceptable_types[-1].split('/')[-1].upper()
#     if not upload.content_type in acceptable_types:
#         Error = True
#         ErrorMsg.append( ValidationError( (u'L\'extension du fichier doit être {}.'.format( str_acceptable_types )), code='filetype' ) )
#     if upload.size > max_size:
#         Error = True
#         ErrorMsg.append(  ValidationError( (u'La taille du fichier ne doit pas excéder {} Mo.' .format( max_size/1000000 )), code='filezize' ) )
#     if Error:
#         raise ValidationError(ErrorMsg)
#
#     # if all of this pass then download temporary file and use magic to dertermine type
#
#     try:
#         upload.name = remove_accents( upload.name )
#     except:
#         if upload.content_type == 'application/pdf':
#             upload.name = u"file.pdf"
#         elif upload.content_type == 'image/jpeg':
#             upload.name = u"file.jpeg"
#         elif upload.content_type == 'image/png':
#             upload.name = u"file.png"
#         else:
#             upload.name = u"file.bug"
#
#     # Make uploaded file accessible for analysis by saving in tmp
#     tmp_path = 'tmp/{}.{}'.format( generate_slug_id(), upload.name.split('.')[-1] )
#     default_storage.save(tmp_path, ContentFile(upload.file.read()))
#     full_tmp_path = os.path.join(settings.MEDIA_ROOT, tmp_path)
#     # Get MIME type of file using python-magic and then delete
#     file_type = magic.from_file(full_tmp_path, mime=True)
#     default_storage.delete(tmp_path)
#     if file_type not in acceptable_types:
#         raise ValidationError(  (u'Le fichier doit être de type: {}.'.format( str_acceptable_types )), code='filetype' )
#
#
#
#
# class headForm(forms.Form):
#     upload = forms.ImageField(label=u'Justificatif',validators=[image_validator], required=True, help_text=mark_safe("YOLO.") )
