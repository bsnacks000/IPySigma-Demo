
var browser_room = io('http://localhost:3000/browser')
var main_room = io('http://localhost:3000/main') // connect a socket to the main room


//TODO loki init here
var idbAdapter = new LokiIndexedAdapter();
var db = new loki("test.db", { adapter: idbAdapter });
var responses = db.addCollection('responses');

//FIXME loki storage/lookup needs to change for graphs - 
// available graphs should be stored by title as some kind of selectable list view on the page
// For now.. we just hit python every time we load 




$('#load-main-graph').submit(function(e){
    e.preventDefault()

    var title = $('#graph-title').val();
    console.log(title);


    query_loki('main_graph').then(function(db_query){       //query object from loki... if not in db emit request to kernel
        
        if (db_query.length != 0){
            
            //FIXME pass here for now... should hit the memory cache/db first before emit

        } else {
            var g = responses.data[0].py_obj_name

            main_room.emit('get-graph', {'title': title,'graph_name': g });  //FIXME need to figure out how to properly query loki for py_obj_name 
        }
    });
});


// this listener receives the python object reference pushes to loki, the browser instance uses this to connect to the python object
//FIXME need to be able to be able to handle if user goes to localhost3000 without the pyobj reference
browser_room.on('pyobj-ref-to-browser', (obj_ref)=>{
    console.log(obj_ref);  //TODO need to make sure this request is correct 
    $('title').text(obj_ref.py_obj_name)
    push_py_obj_to_loki(obj_ref);
})


main_room.on('message-reply', function(msg){               // handle the reply message
    // TODO: error check both msg status and that return value is the correct format
    // this parse and error checking should probably move to the server

    
    console.log(msg);
    
    var msg_title = msg.title;
    var m = msg.data.user_expressions[msg_title].data['text/plain']
    graph_data = JSON.parse(m.replace(/'/g,""));

    console.log(graph_data) 

    //push the response into the database
    //push_to_loki(msg);

    // create custom html table header

    var graph_data_extra_filter = [
    'color', 'size', 'x', 'y',
    'id', 'label', 'node_type', 
    'sigma_between_central', 'sigma_deg_central','sigma_pagerank'
]
    $('#htmlTable > thead').empty()
    $('#htmlTable > thead').append(make_table_header(extra_headers(graph_data, graph_data_extra_filter)))


    $('#graphTitle').text(msg.title)
    $("#graphContainer").empty()
    $("#controlContainer").css('visibility','visible')


     var s = make_graph(graph_data);
     s.startForceAtlas2(forceAtlasConfig);


    $("#pauseForceAtlas").on('click', function(event){
        if (s.isForceAtlas2Running())
            s.stopForceAtlas2();
        else
            s.startForceAtlas2();
    });


    $('#toggleInspector').on('click', function(event){
        $('#htmlTableWrapper').toggle(700)
    });


    $("#htmlTable").on('click','.rm-btn', function(event){
        $(this).closest('tr').remove();
    });

    // exports to local Downloads folder using the jquery plugin
    $("#exportButton").on('click',function(event){
        $("#htmlTable").tableToCSV();
    });


})


// remove a row from the table - remove header if empty


// Loki helpers -- current version does not use these methods

// loki helper functions that parses and pushes
function push_py_obj_to_loki(py_obj){
    responses.insert(py_obj);
    db.saveDatabase();
}


function push_to_loki(msg){
    responses.insert(msg.user_expressions);
    db.saveDatabase();
}

function query_loki(res_var){
    q_obj = {};
    q_obj[res_var] = {'$contains' : 'data'};  // checks to see if key name is in collection
    return Promise.resolve(responses.find(q_obj));
}

function show_loki_responses(){
    return JSON.stringify(responses.data)
}




// Sigma make_graph -- this will all get moved to its own module... 

// code from the sigmajs API documentation...
// adds neighbors method to sigma factory class -> populates allNeighborsIndex
sigma.classes.graph.addMethod('neighbors', function(nodeId) {
    var k;
    var neighbors = {};
    var index = this.allNeighborsIndex[nodeId] || {};

    for (k in index)
        neighbors[k] = this.nodesIndex[k];

    return neighbors;
});


var forceAtlasConfig = {
    linLogMode: false,
    outboundAttractionDistribution: true,
    startingIterations: 12, // maybe figure out how to scale these for size of graph
    iterationsPerRender: 20,
    gravity:2.25
}

function make_graph(graph_data){


    var s = new sigma({
            graph: graph_data.graph,
            container: 'graphContainer',
            renderers: [{
                container: document.getElementById('graphContainer'),
                type: 'canvas'
            }],
            settings: {
              drawEdges: true,
              drawLabels: false,
              doubleClickEnabled: false
            }
        });


    // code from the sigmajs API documentation
    // binding events for neighbors - save original color
    // Calling refresh() on each callback alters the graph
    s.graph.nodes().forEach(function(n) {   // archive original colors
        n.originalColor = n.color;
    });

    s.graph.edges().forEach(function(e) {
        e.originalColor = e.color;
    });

    s.bind('clickNode', function(e) {
        var nodeId = e.data.node.id;
        var toKeep = s.graph.neighbors(nodeId); // get Neighbor indexes on clicked nodes

        toKeep[nodeId] = e.data.node;

        s.graph.nodes().forEach(function(n) {   // alter node colors for not clicked
          if (toKeep[n.id])
            n.color = n.originalColor;
          else
            n.color = '#eee';
        });

        s.graph.edges().forEach(function(e) {   // alter edge colors; transparent for not clicked, blue for clicked
          if (toKeep[e.source] && toKeep[e.target])
            e.color = 'rgba(27, 115, 186, 0.90)';
          else
            e.color = 'rgba(1, 1, 1, 0.1)';
        });

        s.refresh();
    });

    s.bind('clickStage', function(e) {         // on single click away convert back
        s.graph.nodes().forEach(function(n) {
          n.color = n.originalColor;
        });

        s.graph.edges().forEach(function(e) {
          e.color = e.originalColor;
        });


        s.refresh();
    });


    // binding for html table
    s.bind('doubleClickNode', function(e){
        
        var extra_filter_mask = [
            'originalColor', 'read_cam0:size','read_cam0:x',
            'read_cam0:y','renderer1:size','renderer1:x','renderer1:y',
            'size', 'x', 'y', 'color', 'id', 'label', 'node_type',
            'sigma_between_central', 'sigma_deg_central', 'sigma_pagerank'
        ]

        var data = {
            id: "<td>" + e.data.node.id + "</td>",
            label: "<td>"+ e.data.node.label + "</td>",
            ntype: "<td>"+e.data.node.node_type + "</td>",
            betw: "<td>"+e.data.node.sigma_between_central+ "</td>",
            deg: "<td>"+e.data.node.sigma_deg_central+ "</td>",
            pager:"<td>"+ e.data.node.sigma_pagerank+ "</td>"
        };

        

        // append the node row
        $('#htmlTable > tbody').append(make_table_row(e, data, extra_columns(e, extra_filter_mask)));
    

    });

    return s; // return the sigma instance to outer scope..
}



function extra_headers(graph_data, graph_data_extra_filter){

    var extras = Object.keys(graph_data.graph.nodes[0]).filter((header)=>{
        return graph_data_extra_filter.indexOf(header) === -1;
    }).sort();

    return extras;   
}


function make_table_header(extra_headers){
    

    var tr = "<tr id='headerRow'> <th>id</th> <th>label</th> <th>node_type</th> <th>betweeness</th>" + 
    "<th>degree</th><th>pagerank</th> <th> remove? </th>";


    for(var i=0; i < extra_headers.length; i++)
        tr += "<th>" + extra_headers[i] + "</th>"

    tr += '</tr>'
    return tr
}



function extra_columns(e, extra_filter_mask){

    var extras = Object.keys(e.data.node).filter(function(header){
        return extra_filter_mask.indexOf(header) === -1;
    }).sort();

    return extras;
}



function make_table_row(e, data, extra_columns){
    
    // helper to create a table row dynamically - takes in data object // returns a tr string 
    var removeButton = "<td><button type=button class='rm-btn'>remove</button><td>" ;
    var tr = "<tr>" + data.id + data.label + data.ntype + data.betw + data.deg + data.pager;

    for(var i=0; i < extra_columns.length; i++)
        tr += "<td>" + e.data.node[extra_columns[i]] + "</td>"

    tr += removeButton + '</tr>'
    return tr 

}