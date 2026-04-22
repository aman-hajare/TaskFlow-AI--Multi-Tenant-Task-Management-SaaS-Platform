def task_assigned_template(user_name: str, task_title: str):

    return f""" 
    Hello {user_name},
    
    You have been assigned a new task in TaskFlow AI.
    
    Task: {task_title}
    
    Please login to the dashboard to view details.
    
    Regards,
    TaskFlow AI
    """
