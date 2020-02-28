import json
import requests
import os
import re
from datetime import datetime


todos_link = 'https://json.medrating.org/todos'
users_link = 'https://json.medrating.org/users'

todos_json_file = requests.get(todos_link)
users_json_file = requests.get(users_link)

users = json.loads(users_json_file.text)
todos = json.loads(todos_json_file.text)



def create_report_file(user, completed, others):
	report_pattern = '{} <{}> {}\n{}\n\nЗавершенные задачи:\n{}\n\nОставшиеся задачи:\n{}'
	open(user['username'], 'x').write(report_pattern.format(
		user['name'],
		user['email'],
		datetime.now().strftime('%d.%m.%Y %H:%M'),
		user['company']['name'],
		('\n'.join(completed[user['id']]) if user['id'] in completed else 'Задач нет'),
		('\n'.join(others[user['id']]) if user['id'] in others else 'Задач нет'),
		)
	)


def main():
	try:
		os.mkdir('tasks')
	except FileExistsError:
		pass
	os.chdir('tasks')

	completed = {}
	others = {}

	for todo in todos:
		if todo['completed'] is True:
			if completed.get(todo['userId']):
				completed_tasks = completed[todo['userId']]
				completed_tasks.append(todo['title'] if len(todo['title']) < 50
													else todo['title'][:50] + '...')
			else:
				completed[todo['userId']] = [todo['title'] if len(todo['title']) < 50
														else todo['title'][:50] + '...']
		else:
			if others.get(todo['userId']):
				others_tasks = others[todo['userId']]
				others_tasks.append(todo['title'] if len(todo['title']) < 50
												else todo['title'][:50] + '...')
			else:
				others[todo['userId']] = [todo['title'] if len(todo['title']) < 50
														else todo['title'][:50] + '...']

	for user in users:
		try:
			create_report_file(user=user, completed=completed, others=others)
		except FileExistsError:
			file = open(user['username'], 'r')
			search_date = re.search(r'\d{2}.\d{2}.\d{4} \d{2}:\d{2}', file.read())
			rand_digit = datetime.now().strftime('%S')
			new_file_name = user['username'] + '_' + search_date.group(0) + rand_digit
			os.rename(user['username'], new_file_name)
			create_report_file(user=user, completed=completed, others=others)
	return print("It's done")


if __name__ == '__main__':
	main()