def create_issue(summary, description, project='AST'):
    print('[JIRA] create_issue', summary)
    return {'key':'AST-123', 'url':'https://jira.example/AST-123'}
