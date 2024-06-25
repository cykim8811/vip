const socket = io.connect();

const screen = document.getElementById('screen');


// class InstanceWrap{
//     constructor(id){
//         this.id = id;
//         this.html = "";
//         this.element = null;
//     }
// }


function sleep(t){return new Promise(resolve=>setTimeout(resolve, t));}

let last_req_id = 100000000;
const req_queue = [];
async function request(data){
    return new Promise(function(res, rej){
        const req_id = ++last_req_id;
        socket.emit('request_data', {msg_id: req_id, data: data});
        req_queue.push({msg_id: req_id, resolve: res});
        setTimeout(rej, 1000, {data: data, req_id: req_id});
    });
}
    
socket.on('response', function(msg){
    for (let i=0; i<req_queue.length; i++){
        if (req_queue[i].msg_id == msg.msg_id){
            req_queue[i].resolve(msg.data);
            req_queue.splice(i, 1);
            break;
        }
    }
});

let drag = {target: null, dx: 0, dy: 0, isDragging: false, dropTo: null};

function getId(element){
    while (!element.classList.contains('vipinstance')){element = element.parentElement;}
    for (let i=0; i<element.classList.length; i++){
        if (element.classList[i].slice(0, "vipinstance".length) == "vipinstance" && element.classList[i].length > "vipinstance".length){
            let instanceId = 1 * element.classList[i].slice("vipinstance".length);
            return instanceId;
        }
    }
    return -1;
}

async function updateVariableBuiltin(element, value){
    let owner = element;
    while (!(owner.parentElement == screen || owner.parentElement.classList.contains('vipinstance'))){
        owner = owner.parentElement;
    }
    if (owner.parentElement == screen){
        await request({type: 'update_member_builtin', instanceId: null, member: getId(element), value: value});
        refreshInstance(getId(element));
    }else{
        let ownertext = owner.classList[1].split('.');
        await request({type: 'update_member_builtin', instanceId: 1 * ownertext[0], member: ownertext[1], value: value});
        refreshInstance(getId(owner));
    }
}

async function updateVariable(element, instanceId){
    let owner = element;
    while (!(owner.parentElement == screen || owner.parentElement.classList.contains('vipinstance') || owner.classList.contains('vipmember'))){
        owner = owner.parentElement;
    }
    let ownertext = owner.classList[1].split('.');
    await request({type: 'update_member', owner: 1 * ownertext[0], member: ownertext[1], instanceId: instanceId});
    refreshInstance(1 * ownertext[0]);
}

function bringFront(element){
    element.parentElement.appendChild(element);
}

function preprocess(element, isRoot){
    if (isRoot){
        element.style.position = "absolute";
    }else{
        element.addEventListener('mousedown', async function(ev){
            ev.stopPropagation();
        });
    }
    
    element.addEventListener('mouseenter', async function(ev){
        ev.stopPropagation();
        // TODO: Change borders of ALL elements with same id
//         if (!element.originalBorder){
//             element.originalBorder = element.style.border;
//         }
        emphasize(getId(element))
        element.parentElement.dispatchEvent(new Event('mouseleave', { 'bubbles': true }));
    });
    element.addEventListener('mouseleave', async function(ev){
        element.style.border = element.originalBorder;
        unemphasize(getId(element))
        element.parentElement.dispatchEvent(new Event('mouseenter', { 'bubbles': true }));
    });
    if (element.classList.contains('draggable')){  // Draggable
        element.addEventListener('mousedown', async function(ev){
            ev.stopPropagation();
            bringFront(element);
            if (drag.target == null){
                drag.isDragging = false;
                drag.target = element;
                drag.dx = element.getBoundingClientRect().left - ev.clientX;
                drag.dy = element.getBoundingClientRect().top - ev.clientY;
                
                if (drag.target.parentElement != screen){
                    let ownertext = drag.target.parentElement.classList[1].split('.');
                    let newInstId = await request({type: 'unmember', owner: 1 * ownertext[0], member: ownertext[1]});
                    
                    refreshInstance(getId(drag.target));
                    
                    drag.target.parentElement.removeChild(drag.target);
                    let newHTML = await request({type: 'render', instanceId: newInstId});
                    let newElem = parseHTML(newHTML);
                    
                    newElem.style.position = 'absolute';
                    
                    screen.appendChild(newElem);
                    drag.target = newElem;
                    
                    drag.target.style.left = (ev.clientX + drag.dx) + "px";
                    drag.target.style.top = (ev.clientY + drag.dy) + "px";
                }
                drag.target.style.opacity = 0.8;
                drag.isDragging = true;
            }
        });
    }
}
document.addEventListener('mousemove', async function(ev){
    if (drag.target != null && drag.isDragging == true){
        drag.target.style.position = "absolute";
        drag.target.style.left = (ev.clientX + drag.dx) + "px";
        drag.target.style.top = (ev.clientY + drag.dy) + "px";
        
        drag.target.style.display = 'none';
        let noneList = document.getElementsByClassName('vipnone');
        for (let i=0; i<noneList.length; i++){
            noneList[i].style.border = '1px solid black'; // TODO: Make None's border customizable
            noneList[i].style.backgroundColor = '';
            noneList[i].style.filter = '';
        }
        drag.dropTo = null;
        let hover = document.elementFromPoint(ev.clientX, ev.clientY);
        if (hover.classList.contains('vipnone')){
            hover.style.border = '1px solid blue';
            hover.style.backgroundColor = 'rgb(130, 130, 180)';
            hover.style.filter = 'drop-shadow(1px 1px 2px rgba(90, 90, 140))';
            drag.dropTo = hover;
        }
        drag.target.style.display = '';
    }
});
document.addEventListener('mouseup', function(ev){
    if (drag.dropTo != null){
        updateVariable(drag.dropTo, getId(drag.target));
        drag.dropTo = null;
        drag.target.remove();
    }
    if (drag.target){
        drag.target.style.opacity = 1;
    }
    drag.target = null;
    drag.isDragging = false;
});

function refreshInstance(instanceId){
    let elemList = document.getElementsByClassName('vipinstance' + instanceId);
    let rootList = [];
    for (let i=0; i<elemList.length; i++){
        let rootElem = elemList[i];
        while (rootElem.parentElement != screen) {rootElem = rootElem.parentElement;}
        if (!rootList.includes(rootElem)){
            rootList.push(rootElem);
        }
    }
    for (let rootElem of rootList){
        refreshElement(rootElem);
    }
}

function emphasize(instanceId){
    let elemList = document.getElementsByClassName('vipinstance' + instanceId);
    for (let i=0; i<elemList.length; i++){
        let element = elemList[i];
        if (element.originalBorder == null){
            element.originalBorder = element.style.border;
        }
        
        // element.style.border="1px solid orange";
        element.classList.add('vipemphasize');
    }
}

function unemphasize(instanceId){
    let elemList = document.getElementsByClassName('vipinstance' + instanceId);
    for (let i=0; i<elemList.length; i++){
        let element = elemList[i];
        element.style.border=element.originalBorder;
        element.classList.remove('vipemphasize');
    }
}
async function refreshElement(elem){
    let refElem = await request({type: 'render', instanceId: getId(elem)});
    let newElem = parseHTML(refElem);

    let lastLeft = elem.getBoundingClientRect().left;
    let lastTop = elem.getBoundingClientRect().top;

    newElem.style.left = lastLeft - (1 * elem.style.marginLeft.slice(0, -2)) + 'px';
    newElem.style.top = lastTop - (1 * elem.style.marginTop.slice(0, -2)) + 'px';
    
    elem.replaceWith(newElem);
}

async function call(element, ev){
    let owner = element;
    let newId = await request({type: 'call', instanceId: getId(element)});
    let newHTML = await request({type: 'render', instanceId: newId});
    let newElem = parseHTML(newHTML);

    newElem.style.position = 'absolute';

    screen.appendChild(newElem);
    drag.target = newElem;

    drag.dx = -0.5 * newElem.clientWidth;
    drag.dy = -21;
    
    drag.target.style.left = (ev.clientX + drag.dx) + "px";
    drag.target.style.top = (ev.clientY + drag.dy) + "px";
    
    drag.isDragging = true;
}

let createPos = {left: 5, top: 5};

function parseHTML(html){
    let newelement = document.createElement('div');
    newelement.innerHTML = html;
    rootelement = newelement.children[0];
    vipinstanceList = rootelement.getElementsByClassName('vipinstance');
    editableList = rootelement.getElementsByClassName('editable');
    callableList = rootelement.getElementsByClassName('vipcall');
    
    rootelement.style.left = createPos.left + "px";
    rootelement.style.top = createPos.top + "px";
    createPos.left += 24;
    createPos.top += 24;
    
    preprocess(rootelement, true);
    for (let i=0; i<vipinstanceList.length; i++){
        preprocess(vipinstanceList.item(i), false);
    }
    for (let i=0; i<editableList.length; i++){
        editableList.item(i).addEventListener('mousedown', function(ev){ev.stopPropagation();});
    }
    for (let i=0; i<callableList.length; i++){
        let ftnManager = callableList.item(i);
        while (!ftnManager.classList.contains('vipinstance')){
            ftnManager = ftnManager.parentElement;
        }
        let owner = ftnManager.parentElement;
        while (!(owner == null || owner.classList.contains('vipinstance'))){
            owner = owner.parentElement;
        }
        if (owner != null){ // If this callable is a method
//             console.log('method', 'owner:', getId(ftnManager), 'self:', getId(owner));
            request({type: 'update_member', owner: getId(ftnManager), member: 'self', instanceId: getId(owner)});
        }
        callableList.item(i).addEventListener('mousedown', function(ev){
            ev.stopPropagation();
            call(this, ev);
        });
    }
    
    return rootelement;
}

function appendHTML(html){
    let rootelement = parseHTML(html);
    screen.appendChild(rootelement);
    return rootelement;
}

socket.on('connect', async function(){
    console.log("Connected");
    memory_id = await request({type: 'memory'});
    for (let id of memory_id){
        let newHTML = await request({type: 'render', instanceId: id});
        appendHTML(newHTML);
    }
});

socket.on('message', function(msg){
    
});

