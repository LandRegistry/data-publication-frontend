from flask_wtf import Form
from wtforms import TextField, IntegerField, SelectField, RadioField
from wtforms.validators import ValidationError, Required, Length, NumberRange, Regexp

import datetime

E_MAIL_REGEX = "^(?:[a-zA-Z0-9'_-]+(?:\.[a-zA-Z0-9'_&-]+)*)@" \
               "(?:(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+" \
               "[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?)$"

class RequiredIfEquals(object):

    def __init__(self, conditional_field, conditional_value, message=None):
        self.conditional_field = conditional_field
        self.conditional_value = conditional_value
        if message is None:
            message = u'Required field'
        self.message = message

    def __call__(self, form, field):
        conditional = form._fields.get(self.conditional_field)
        if conditional.data is not None and conditional.data.strip() == self.conditional_value:
            if field.data is None or field.data.strip() == '':
                raise ValidationError(self.message)


class ValidateDate(object):

    def __init__(self, day_field, month_field, check_future, invalid_message=None,
                 future_message=None):
        self.day = day_field
        self.month = month_field
        self.check_future = check_future
        if not invalid_message:
            invalid_message = u'Date is not a valid date.'
        self.invalid_message = invalid_message
        if not future_message:
            future_message = u'Date is in the future'
        self.future_message = future_message

    def __call__(self, form, field):
        day = form._fields.get(self.day)
        month = form._fields.get(self.month)
        year = field
        try:
            dob = datetime.datetime(year.data, month.data, day.data)
        except ValueError:
            if not (form.day.errors or form.month.errors or form.year.errors):
                raise ValidationError(self.invalid_message)

        if self.check_future:
            now = datetime.datetime.now()
            if dob > now:
                raise ValidationError(self.future_message)


class RequiredUnless(object):

    def __init__(self, alt_field, message=None):
        self.alt_field = alt_field
        self.message = message

    def __call__(self, form, field):
        alternative = form._fields.get(self.alt_field)
        if alternative.data is None or alternative.data.strip() == '':
            if field.data is None or field.data.strip() == '':
                if self.message is None:
                    self.message = u'Required unless {} is completed'.format(
                        form._fields.get(self.alt_field).label.text)
                raise ValidationError(self.message)


class UserTypeForm(Form):
    user_type = RadioField('User Type', choices=[('Private individual', 'Private individual'),
                                                 ('Company', 'Company')])


class PersonalForm(Form):
    title = SelectField('Title', choices=[('Dr', 'Dr.'), ('Lady', 'Lady'), ('Lord', 'Lord'),
                                          ('Miss', 'Miss.'), ('Mr', 'Mr.'), ('Mrs', 'Mrs.'),
                                          ('Ms', 'Ms.'), ('Other', 'Other'), ('Prof', 'Prof.')])
    other_title = TextField('If \'Other\' please specify',
                            validators=[Length(max=60),
                                        RequiredIfEquals(conditional_field='title',
                                                         conditional_value='Other',
                                                         message='\'Other\' title is required')])

    first_name = TextField('First Name(s)/Given Name(s)',
                           validators=[
                               Length(max=60),
                               Required(message="First Name(s)/Given Name(s) is required")])
    last_name = TextField('Last Name/Family Name',
                          validators=[
                              Length(max=60),
                              Required(message="Last Name/Family Name is required")])
    username = TextField('Username',
                         validators=[
                             Length(max=60), Required(message="Username is required")])

    current_year = datetime.date.today().year
    oldest_year = current_year - 125
    day = IntegerField('day',
                       validators=[
                           Required(message="day is required"),
                           NumberRange(min=1, max=31, message="Day must be between 1 and 31")])
    month = IntegerField('month',
                         validators=[
                             Required(message="month is required"),
                             NumberRange(min=1, max=12, message="Month must be between 1 and 12")])
    year = IntegerField('year',
                        validators=[
                            Required(message="year is required"),
                            NumberRange(min=oldest_year, max=current_year,
                                        message="Year must be between {} and {}".format(
                                            oldest_year, current_year)),
                            ValidateDate(day_field='day', month_field='month', check_future=True)])


class CompanyForm(PersonalForm):
    company_name = TextField('Company Name',
                             validators=[
                                 Length(max=60), Required(message="Company Name is required")])


class AddressForm(Form):
    address_line_1 = TextField('Address Line 1',
                               validators=[
                                   Length(max=60), Required(message="Address Line 1 is required")])
    address_line_2 = TextField('Address Line 2', validators=[Length(max=60)])
    address_line_3 = TextField('Address Line 3', validators=[Length(max=60)])
    city = TextField('Town/City', validators=[Length(max=60)])
    region = TextField('State/Province/Region/County', validators=[Length(max=60)])
    postal_code = TextField('ZIP/Postal Code/Postcode', validators=[Length(max=60)])
    country = TextField('Country',
                        validators=[Length(max=60), Required(message="Country is required")])


class TelForm(Form):
    landline = TextField('Telephone (Landline)',
                         validators=[Length(max=60), RequiredUnless(alt_field='mobile')])
    mobile = TextField('Telephone (Mobile)',
                       validators=[Length(max=60), RequiredUnless(alt_field='landline')])
    email = TextField('E-mail',
                      validators=[Length(max=60),
                                  Required(message="E-mail is required"),
                                  Regexp(E_MAIL_REGEX, message='Invalid e-mail address format')])


class CompanyTelForm(TelForm):
    landline = TextField('Telephone (Landline)',
                         validators=[Length(max=60),
                                     Required(message='Telephone (Landline) is required')])
    mobile = TextField('Telephone (Mobile)',
                       validators=[Length(max=60)])
