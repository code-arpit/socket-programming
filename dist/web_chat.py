web_chat_html = """
    <!DOCTYPE html>
    <html>
      <head>
        <title>Chat</title>
      </head>
      <body>
        <h1>WebSocket Chat</h1>
        <h2>User: b62b3790-7601-4acb-8f43-6e2dda389fee</h2>
        <form action="" onsubmit="sendMessage(event)">
          <input type="text" id="messageText" autocomplete="off" />
          <button>Send</button>
        </form>
        <ul id="messages"></ul>
        <script>
          let conversation_id = ""
          let message_id = ""
          let client_id = ""
          let client_port = ""
          let time = ""
          let sender = ""
          let ws_url = 'ws://192.168.49.1:8007/ws/eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzExNjIwMTk2LCJpYXQiOjE3MTE2MTI5OTYsImp0aSI6Ijk1ZGZlOWQ2MWFkMjRiMjRhNTViNzY0MjAzNWE1YjMxIiwidXNlcl9pZCI6Ijg2OWRlNjFlLWIxMzEtNGU2Yi1hY2M2LWZkMTBkZjY0NjIxZiJ9.pgbRr7TNHMCZ-Ik_TB04PfHZtc7eptdkepydmfpjoqE'
          if (conversation_id  != ''){
            ws_url = ws_url + `?conversation_id=${conversation_id}`;
          }
          var ws = new WebSocket(
            ws_url,
          )
          ws.onmessage = function (event) {
            var messages = document.getElementById('messages')
            var message = document.createElement('li')
            let json_content = JSON.parse(event.data)
            var content = document.createTextNode(json_content.message)
            conversation_id = json_content.conversation_id
            message_id = json_content.message_id
            client_id = json_content.client_id
            client_port = json_content.client_port
            time = json_content.time
            sender = json_content.sender
            
            message.appendChild(content)
            messages.appendChild(message)
          }
          function sendMessage(event) {
            var input = document.getElementById('messageText')
            var message = {
              conversation_id: conversation_id,
              message_id: message_id,
              message: input.value,
              client_id: client_id,
              client_port: client_port,
              time: time,
              sender: sender
            }
            console.log(message)
            ws.send(JSON.stringify(message))
            input.value = ''
            event.preventDefault()
          }
        </script>
      </body>
    </html>
"""
