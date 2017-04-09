'use strict';
const services = require('@jupyterlab/services');
const ws = require('ws');
const xhr = require('xmlhttprequest');

const express = require('express')
const app = express();
const server = require('http').Server(app);
const io = require('socket.io')(server);

const HTTP_PORT = 3000; // port number for local express app

// override as part of jupyterlab/services
global.XMLHttpRequest = xhr.XMLHttpRequest;
global.WebSocket = ws;


// simple server for our express/socket.io app
server.listen(HTTP_PORT, () => {
    console.log('express listening on localhost:' + HTTP_PORT)
});

app.use(express.static(__dirname + '/browser'));

app.get('/', function (req, res) {
    res.sendFile(__dirname + '/browser/index.html');
})

//FIXME: proper error handling needed throughout the node server! 

let main_room = io.of('/main');
let py_room = io.of('/py');
let browser_room = io.of('/browser');

let connections = {};
//let current_browser_id = null; // temp variable that stores a 
let py_object_names = [];

main_room.on('connection', (socket)=>{
    

    services.Kernel.listRunning().then((kernelModels)=>{  //token passed in

        let options =  {name:kernelModels[0].name }

        services.Kernel.connectTo(kernelModels[0].id,options).then((kernel)=>{
            console.log('user ' + socket.id + ' connected to kernel: '+ kernelModels[0].id)

            // main sockets to communicate with Python IPySig here:
            socket.on('get-graph', (msg) => {     
                
                // msg schema {'title': 'title_name', 'graph_name': graph_name } 
                
                //TODO:: error check msg here

                let future = kernel.requestExecute({ code:'',
                    user_expressions:{[`${msg.title}`]:`IPySig.export_graph_instance('${msg.graph_name}')`}  
                });
                
                future.onReply = function(reply){
                    
                    main_room.to(socket.id).emit('message-reply', {'data': reply.content, 'title': msg.title});   // all replies get sent back through a single channel
                }
            });

            socket.on('disconnect', ()=>{
                console.log('user '+ socket.id + ' diconnected from kernel: '+ kernelModels[0].id)
                // can maybe emit here to fetch the browser data store and save it to disk


            });

        });
        //need to close connection to kernel via services.Kernel somehow

    }).catch((err)=>{
        console.log(err);
    });
  
});


browser_room.on('connection', (socket)=>{

    // this maintains a private namespace for for browser-server communication  

    connections[socket.id] = py_object_names.pop()
    console.log('browser_connected: '+ socket.id)
    
    browser_room.to(socket.id).emit('pyobj-ref-to-browser', {'py_obj_name': connections[socket.id]})
});



py_room.on('connection', (socket)=>{
    // this room connects with an IPySig object on the python kernel

    socket.on('py-object-name', (py_obj_name)=>{

        let msg = { 'echo_name': py_obj_name ,'http_port': HTTP_PORT.toString()};
        
        py_object_names.push(py_obj_name);
        // hits python client-side callback and send the HTTP_PORT number
        socket.emit('pyconnect_response', msg); 
    });
    
});


