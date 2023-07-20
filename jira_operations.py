from jira import JIRA
from settings import *


def jira_create_task(summary, description, assignee=jira_assignee):
    jira_options = {'server': jira_server}
    jira = JIRA(options=jira_options, basic_auth=(jira_username, jira_key))
    new_issue = jira.create_issue(project="CTP", summary=summary, description=description, issuetype={'name': 'Task'},
                      assignee={"name": assignee}, customfield_11502=jira_account, customfield_10109=jira_epic_link,
                      customfield_11903=[{"value": jira_scope}], fixVersions=[{"id": jira_fix}],
                      priority={"name": jira_priority})

    return new_issue.key
