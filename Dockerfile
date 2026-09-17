FROM docker.io/redmine:latest

# Replace the english locales file with one that replaces "issue" with "ticket"
COPY en.yml /usr/src/redmine/config/locales/en.yml