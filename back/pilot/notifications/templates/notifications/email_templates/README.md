# MJML

We use the MJML framework to generate HTML email templates
https://mjml.io/

# **WARNING**
The HTML generated does not have i18n Django template tags on top of them. And at the moment I did not find a solution to have those tags in mjml file.
Add these tags manually or you will face silent fails during render.

Pay special attention at HTML generated : linebreaks may be inserted in translated string, breaking "trans" tag in template.
If using mjml desktop app do not "copy Html" but "export html file" and copy paste in IDE without reformating the code (translation string may break)


# Documentation:
https://mjml.io/documentation/

# Github
https://github.com/mjmlio/mjml

# Tooling
Mjml provides JS tools to build .html files from .mjml files but also super useful desktop app for various OSes
"mjml" js dependency is not in our package.json at the moment (we use desktop app)
https://mjmlio.github.io/mjml-app/

