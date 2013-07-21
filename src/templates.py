from conditional_template import ConditionalTemplate as Template
import sessions

def replyTemplate (user, message):
 #Given an user and message, returns it as a reply.
 template = Template(sessions.current_session.config['templates']['reply'])
 mapping = {}
 mapping['message'] = message
 mapping['user'] = user
 return template.Substitute(mapping)

def retweetTemplate (user, message):
 #Given an user and message, returns it as a retweet.
 template = Template(sessions.current_session.config['templates']['retweet'])
 mapping = {}
 mapping['message'] = message
 mapping['user'] = user
 return template.Substitute(mapping)
