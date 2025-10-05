import requests

api_url = "http://192.168.0.105:8501/process_ticket"

def submit_ticket(ticket_text):
    try:
        response = requests.post(api_url, json={"text": ticket_text}, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to the AI API server. Please ensure it is running and accessible."}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please check server status and network connection."}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Example usage
if __name__ == "__main__":
    ticket_data = "Sample ticket data"
    result = submit_ticket(ticket_data)
    print(result)