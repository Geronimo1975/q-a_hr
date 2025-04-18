import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'driver_recruitment.settings')
django.setup()

from recruitment.models import QuestionStage, Question

# Clear existing data
print("Clearing existing stages and questions...")
Question.objects.all().delete()
QuestionStage.objects.all().delete()

# Create stages
print("Creating stages...")
stage1 = QuestionStage.objects.create(stage_number=1, stage_name="Basic Qualifications")
stage2 = QuestionStage.objects.create(stage_number=2, stage_name="Detailed Assessment")
stage3 = QuestionStage.objects.create(stage_number=3, stage_name="Final Qualification")

# Create questions for Stage 1
print("Creating questions for Stage 1...")
Question.objects.create(
    stage=stage1,
    question_text="What is your full name?",
    question_type="name",
    is_required=True,
    order=1
)

Question.objects.create(
    stage=stage1,
    question_text="What is your date of birth?",
    question_type="dob",
    is_required=True,
    order=2
)

Question.objects.create(
    stage=stage1,
    question_text="What is your complete address?",
    question_type="address",
    is_required=True,
    order=3
)

Question.objects.create(
    stage=stage1,
    question_text="What is your phone number?",
    question_type="phone",
    is_required=True,
    order=4
)

Question.objects.create(
    stage=stage1,
    question_text="Do you have a valid driver's license?",
    question_type="boolean",
    is_required=True,
    order=5
)

Question.objects.create(
    stage=stage1,
    question_text="How many years of driving experience do you have?",
    question_type="number",
    is_required=True,
    order=6
)

Question.objects.create(
    stage=stage1,
    question_text="What type of vehicle do you own?",
    question_type="choice",
    choices="Car;Motorcycle;Bicycle;I don't own a vehicle",
    is_required=True,
    order=7
)

Question.objects.create(
    stage=stage1,
    question_text="Are you available to work on weekends?",
    question_type="boolean",
    is_required=True,
    order=8
)

Question.objects.create(
    stage=stage1,
    question_text="What is your preferred working area?",
    question_type="text",
    is_required=True,
    order=9
)

Question.objects.create(
    stage=stage1,
    question_text="How did you hear about this position?",
    question_type="choice",
    choices="Job Board;Social Media;Friend/Family;Company Website;Other",
    is_required=True,
    order=10
)

# Create questions for Stage 2
print("Creating questions for Stage 2...")
Question.objects.create(
    stage=stage2,
    question_text="Please upload a copy of your driver's license",
    question_type="file",
    is_required=True,
    order=1,
    allowed_file_types="jpg,jpeg,png,pdf",
    max_file_size=5
)

Question.objects.create(
    stage=stage2,
    question_text="What are your preferred working hours?",
    question_type="choice",
    choices="Morning (6AM-2PM);Afternoon (2PM-10PM);Night (10PM-6AM);Flexible",
    is_required=True,
    order=2
)

Question.objects.create(
    stage=stage2,
    question_text="How many kilometers do you typically drive per year?",
    question_type="number",
    is_required=True,
    order=3
)

Question.objects.create(
    stage=stage2,
    question_text="Have you worked as a delivery driver before?",
    question_type="boolean",
    is_required=True,
    order=4
)

Question.objects.create(
    stage=stage2,
    question_text="Describe your most recent delivery or driving job",
    question_type="text",
    is_required=False,
    order=5
)

Question.objects.create(
    stage=stage2,
    question_text="Do you have experience with food delivery apps?",
    question_type="boolean",
    is_required=True,
    order=6
)

Question.objects.create(
    stage=stage2,
    question_text="Which food delivery platforms have you worked with?",
    question_type="choice",
    choices="Uber Eats;Lieferando;Wolt;Foodora;Other;None",
    is_required=True,
    order=7
)

Question.objects.create(
    stage=stage2,
    question_text="What is your preferred vehicle for deliveries?",
    question_type="choice",
    choices="Car;Motorcycle;Bicycle;Electric Scooter;On Foot",
    is_required=True,
    order=8
)

Question.objects.create(
    stage=stage2,
    question_text="Are you comfortable with using a smartphone app for deliveries?",
    question_type="boolean",
    is_required=True,
    order=9
)

Question.objects.create(
    stage=stage2,
    question_text="What is your current employment status?",
    question_type="choice",
    choices="Employed Full-time;Employed Part-time;Self-employed;Student;Unemployed",
    is_required=True,
    order=10
)

# Create questions for Stage 3
print("Creating questions for Stage 3...")
Question.objects.create(
    stage=stage3,
    question_text="Please upload a recent photo of yourself",
    question_type="file",
    is_required=True,
    order=1,
    allowed_file_types="jpg,jpeg,png",
    max_file_size=3
)

Question.objects.create(
    stage=stage3,
    question_text="Please upload your CV/resume",
    question_type="file",
    is_required=True,
    order=2,
    allowed_file_types="pdf,doc,docx",
    max_file_size=5
)

Question.objects.create(
    stage=stage3,
    question_text="What is your expected hourly rate (in EUR)?",
    question_type="number",
    is_required=True,
    order=3
)

Question.objects.create(
    stage=stage3,
    question_text="How many hours per week can you work?",
    question_type="number",
    is_required=True,
    order=4
)

Question.objects.create(
    stage=stage3,
    question_text="When can you start working?",
    question_type="text",
    is_required=True,
    order=5
)

Question.objects.create(
    stage=stage3,
    question_text="Do you have a smartphone with a data plan?",
    question_type="boolean",
    is_required=True,
    order=6
)

Question.objects.create(
    stage=stage3,
    question_text="Are you legally eligible to work in Germany?",
    question_type="boolean",
    is_required=True,
    order=7
)

Question.objects.create(
    stage=stage3,
    question_text="What languages do you speak fluently?",
    question_type="choice",
    choices="German;English;German & English;Other",
    is_required=True,
    order=8
)

Question.objects.create(
    stage=stage3,
    question_text="How would you handle a difficult customer situation?",
    question_type="text",
    is_required=True,
    order=9
)

Question.objects.create(
    stage=stage3,
    question_text="Do you consent to a background check?",
    question_type="boolean",
    is_required=True,
    order=10
)

print("Done! Created 3 stages with 10 questions each (30 questions total).")