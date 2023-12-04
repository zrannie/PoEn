# PoEn
Your daily dose of personalized positive content to cheer you up on your calendar

To set up:
1. Get your Google Calendar API credentials from [developer console](https://developers.google.com/workspace/guides/create-credentials?authuser=1) and put into "credentials.json"
2. Verify [Google Calendar access OAuth](https://developers.google.com/workspace/guides/configure-oauth-consent?authuser=1) once to generate your own "token.pickle"
3. Get your OpenAI key and replace the string in the Python script
4. Run script once to check if any bugs
5. If no, set up Crontab (for macOS) to make the script run everyday at certain time, using command:
     crontab -e  ##enter edit mode of crontab
     0 7 * * * /PATHtoyourPython/python /PATHtoyourscript/positive_calendar_event.py >> /PATHtoyourproject/cron.log 2>&1
