# Script for sending alerts from Splunk to eXpress with Vault Integration

## Contains:

- `send_alert` - send alerts
- `send_alert_with_mentions` - send alerts with mentions

## Script Operation Notes
```
| eval event ="___"."Alert"."___"
| rex mode=sed field=event "s/___/\n/g"
```
This is related to Splunk adding quotes, and for their correct removal, a line break is required.

2. To add mentions, the following needs to be included in the alert:
responsible: id, id
Пример:
```
| eval event ="test"."___"."responsible: 2*************************"."___"
| rex mode=sed field=event "s/___/\n/g"
```
Important: there should be a space between "responsible:" and the user "id". Subsequent listing of user ids (1-3) is done using commas, with or without spaces.

3. The script integrates with Vault for secure storage of sensitive data, such as authentication details. Ensure proper Vault configuration and setup of environment variables for secure handling of credentials.
