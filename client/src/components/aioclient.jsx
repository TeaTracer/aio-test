import React from 'react';

export default class Test extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            message_id: 0,
            data: undefined,
            is_error: false
        };
    }

    componentDidMount() {
        var ws = new WebSocket(this.props.server);
        document.cookie = "token=SeCrEtToKen; path=/;";

        ws.onmessage = (event) => {
            var data = JSON.parse(event.data);
            this.setState({"data": data});
            console.log(data);
        };

        var sendRequest = () => {
            var request = {
                jsonrpc: "2.0",
                id: this.state.message_id,
                method: "ping",
                params: undefined
            };
            ws.send(JSON.stringify(request))
            this.setState({"message_id": this.state.message_id + 1});
        }

        ws.onopen = () => {
            setInterval( _ => sendRequest(), 2000);
        }
        ws.onerror = (e) => {
            this.setState({'is_error': true});
            console.log('Error');
        }
      }

    render() {
        return (
            <div>
                <div> Test!!! </div>
                <div> {!this.state.is_error ? this.state.message_id : 'ERROR!'} </div>
            </div>
        );
    }

};
