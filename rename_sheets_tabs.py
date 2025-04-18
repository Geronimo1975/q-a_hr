"""
Instructions for manually setting up the Google Sheet tabs for the Driver Recruitment Application
"""

print("""
Since we're unable to programmatically modify your Google Sheet due to permission restrictions,
here are the manual steps to set up the tabs correctly:

1. Open your Google Sheet at:
   https://docs.google.com/spreadsheets/d/1SwVg13wGY8-yBxv3uzTiaeJ0pAhEPEgRBp_wRdOwluk/edit

2. Right-click on the "Foaie1" tab at the bottom and select "Rename"
   - Rename it to "Stage1"

3. Create two more tabs:
   - Click the "+" button at the bottom left to add a new tab
   - Name it "Stage2"
   - Repeat to create a "Stage3" tab

4. Add these headers to each tab (in row 1, columns A-N):
   - Email
   - Full Name
   - Stage
   - Timestamp
   - Question 1
   - Question 2
   - Question 3
   - Question 4
   - Question 5
   - Question 6
   - Question 7
   - Question 8
   - Question 9
   - Question 10

5. Once the tabs are set up:
   - The system will automatically export questionnaire responses to the appropriate tab
   - Stage 1 answers will go to the Stage1 tab
   - Stage 2 answers will go to the Stage2 tab
   - Stage 3 answers will go to the Stage3 tab

Note: For proper Google Sheets write access, you would need to either:
1. Enable OAuth2 authentication (requires user consent flow)
2. Share the sheet with the service account email: deliverydriver-service-270@translate-457112.iam.gserviceaccount.com

For now, the setup will use read-only access for validation, and we'll show detailed instructions
for enabling write access if needed.
""")