from flask import Flask, redirect, request

app = Flask(__name__)

@app.route('/')
def login_redirect():
    # Redirect to your login page
    return redirect("https://pdn-sqrpmnwxkqz7wf37j52qpygmio6jk2o4.login.gcp.us.pangea.cloud/authorize?state=xxxxxxxxxxxxx")

@app.route('/authorize_callback', methods=['GET', 'POST'])
def authorize_callback():
    if request.method == 'POST':
        # Assuming you want to print the response body
        response = request.get_data()
        print(response)
        return "Response printed successfully."
    else:
        return "Invalid request method."

if __name__ == '__main__':
    app.run(debug=True)
