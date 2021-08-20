const socket = io.connect('http://52.78.66.0:80');

const textbox = document.getElementById('area');
const inputbox = document.getElementById('input');

document.addEventListener('keydown', function(ev){
    if (ev.key == "Enter"){
        socket.emit('message', {'data': inputbox.value});
        textbox.value += '>' + inputbox.value + '\n';
        inputbox.value = '';
    }
});

class InstanceWrap{
    constructor(id){
        this.id = id;
        this.html = "";
        this.element = null;
    }
}

let memory = [];

let last_req_id = 10000000;
const req_queue = [];
async function request(data){
    return new Promise(function(res, rej){
        const req_id = ++last_req_id;
        socket.emit('request_data', {msg_id: req_id, data: data});
        req_queue.push({msg_id: req_id, resolve: res});
        setTimeout(rej, 1000);
    });
}
    
socket.on('response', function(msg){
    for (let i=0; i<req_queue.length; i++){
        if (req_queue[i].msg_id == msg.msg_id){
            req_queue[i].resolve(msg.data);
            req_queue.splice(i);
            break;
        }
    }
});



socket.on('connect', async function(){
    console.log("Connected");
    memory_id = await request({type: 'memory'});
    for (let id of memory_id){
        let instancewrap = new InstanceWrap(id);
        instancewrap.html = await request({type: 'render', instanceId: id});
        memory.push(instancewrap);
    }
});

socket.on('message', function(msg){
    
});