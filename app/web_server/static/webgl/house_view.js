
function HouseRect(x, y, w, h)
{
    this.x = x;
    this.y = y;
    this.w = w;
    this.h = h;
}

function HouseDevices(id, x, y, z)
{
    this.x = x;
    this.y = y;
    this.z = z;
    this.id = id;
}

function House()
{
    this.rooms = new Array();
    this.devices = new Array();

    this.addRoom = function(x, y, w, h)
    {
        this.rooms.push(new HouseRect(x, y, w, h))
    }

    this.addDevice = function(id, x, y, z)
    {
        this.devices.push(new HouseDevices(id, x, y, z))
    }

    this.getBoundingBox = function()
    {
        var min_x = this.rooms[0].x;
        var min_y = this.rooms[0].y;
        var max_x = this.rooms[0].x + this.rooms[0].w;
        var max_y = this.rooms[0].y + this.rooms[0].h;

        for (var i = 1; i < this.rooms.length; i++)
        {
            min_x = Math.min(min_x, this.rooms[i].x);
            min_y = Math.min(min_y, this.rooms[i].y);
            max_x = Math.max(max_x, this.rooms[i].x + this.rooms[i].w);
            max_y = Math.max(max_y, this.rooms[i].y + this.rooms[i].h);
        }

        return HouseRect(min_x, min_y, max_x - min_x, max_y - min_y);
    }

}

var objectsLib = new Object();
objectsLib.cube = [
    // vertex       , normal
    // Z
    -1.0, -1.0,  1.0,  0.0,  0.0,  1.0,
    +1.0, -1.0,  1.0,  0.0,  0.0,  1.0,
    +1.0, +1.0,  1.0,  0.0,  0.0,  1.0,
    +1.0, +1.0,  1.0,  0.0,  0.0,  1.0,
    -1.0, +1.0,  1.0,  0.0,  0.0,  1.0,
    -1.0, -1.0,  1.0,  0.0,  0.0,  1.0,

    +1.0, -1.0, -1.0,  0.0,  0.0, -1.0,
    -1.0, -1.0, -1.0,  0.0,  0.0, -1.0,
    -1.0, +1.0, -1.0,  0.0,  0.0, -1.0,
    -1.0, +1.0, -1.0,  0.0,  0.0, -1.0,
    +1.0, +1.0, -1.0,  0.0,  0.0, -1.0,
    +1.0, -1.0, -1.0,  0.0,  0.0, -1.0,

    // Y
    +1.0, +1.0, -1.0,  0.0,  1.0,  0.0,
    -1.0, +1.0, -1.0,  0.0,  1.0,  0.0,
    -1.0, +1.0, +1.0,  0.0,  1.0,  0.0,
    -1.0, +1.0, +1.0,  0.0,  1.0,  0.0,
    +1.0, +1.0, +1.0,  0.0,  1.0,  0.0,
    +1.0, +1.0, -1.0,  0.0,  1.0,  0.0,

    -1.0, -1.0, +1.0,  0.0, -1.0,  0.0,
    +1.0, -1.0, -1.0,  0.0, -1.0,  0.0,
    +1.0, -1.0, +1.0,  0.0, -1.0,  0.0,
    -1.0, -1.0, -1.0,  0.0, -1.0,  0.0,
    +1.0, -1.0, -1.0,  0.0, -1.0,  0.0,
    -1.0, -1.0, +1.0,  0.0, -1.0,  0.0,

    // X
    +1.0, -1.0, -1.0,  1.0,  0.0,  0.0,
    +1.0, +1.0, -1.0,  1.0,  0.0,  0.0,
    +1.0, +1.0, +1.0,  1.0,  0.0,  0.0,
    +1.0, +1.0, +1.0,  1.0,  0.0,  0.0,
    +1.0, -1.0, +1.0,  1.0,  0.0,  0.0,
    +1.0, -1.0, -1.0,  1.0,  0.0,  0.0,

    -1.0, +1.0, +1.0, -1.0,  0.0,  0.0,
    -1.0, -1.0, -1.0, -1.0,  0.0,  0.0,
    -1.0, -1.0, +1.0, -1.0,  0.0,  0.0,
    -1.0, +1.0, -1.0, -1.0,  0.0,  0.0,
    -1.0, -1.0, -1.0, -1.0,  0.0,  0.0,
    -1.0, +1.0, +1.0, -1.0,  0.0,  0.0,
];

function HouseWallVertexArray(wall_count)
{
    this.vertices_count = wall_count * 6 * 6;
    this.array = new Array(this.vertices_count * 3);
    this.wall_id = 0;

    this.wall = function(x0, y0, x1, y1)
    {
        var stride = 6;
        var offset = 36 * stride * this.wall_id;
        var wall_thickness = 0.1;

        var x = (x0 - 0.5 * wall_thickness);
        var y = (y0 - 0.5 * wall_thickness);
        var z = (0.0);
        var dx = (wall_thickness + x1 - x0);
        var dy = (wall_thickness + y1 - y0);
        var dz = (2.2);

        this.wall_id++;

        for (var i = 0; i < 36; i++)
        {
            // vertice
            this.array[offset + i * stride + 0] = x + dx * (0.5 + 0.5 * objectsLib.cube[i * stride + 0]);
            this.array[offset + i * stride + 1] = y + dy * (0.5 + 0.5 * objectsLib.cube[i * stride + 1]);
            this.array[offset + i * stride + 2] = z + dz * (0.5 + 0.5 * objectsLib.cube[i * stride + 2]);

            // normal
            this.array[offset + i * stride + 3] = objectsLib.cube[i * stride + 3];
            this.array[offset + i * stride + 4] = objectsLib.cube[i * stride + 4];
            this.array[offset + i * stride + 5] = objectsLib.cube[i * stride + 5];
        }

    }

}

function HouseView(output, canvas_id, house)
{
    this.output = output;
    this.canvas = document.getElementById(canvas_id);
    this.house = house;

    this.viewport = new Viewport();
    this.camera = new Camera();

    try
    {
        this.gl = createWebGLXContext(this.canvas);
    }
    catch (msg)
    {
        this.output.error(msg);
        throw msg;
    }

    this.update = function()
    {
        this.viewport.width = this.canvas.width;
        this.viewport.height = this.canvas.height;
        this.viewport.update();

        this.camera.update();

        this.draw()
    }

    this.update_model = function()
    {
        var gl = this.gl;

        var room_count = this.house.rooms.length;
        var wall_count = room_count * 4;

        var wall_vertices = new HouseWallVertexArray(wall_count);

        for (var i = 0; i < room_count; i++)
        {
            var x0 = this.house.rooms[i].x;
            var y0 = this.house.rooms[i].y;
            var x1 = x0 + this.house.rooms[i].w;
            var y1 = y0 + this.house.rooms[i].h;

            wall_vertices.wall(x0, y0, x1, y0);
            wall_vertices.wall(x1, y0, x1, y1);
            wall_vertices.wall(x0, y1, x1, y1);
            wall_vertices.wall(x0, y0, x0, y1);
        }

        this.buffer = gl.createBuffer();
        this.vertices_count = wall_vertices.vertices_count;

        gl.bindBuffer(gl.ARRAY_BUFFER, this.buffer);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(wall_vertices.array), gl.STATIC_DRAW);

        this.update()
    }

    this.draw = function()
    {
        var gl = this.gl;

        gl.viewport(0, 0, gl.drawingBufferWidth, gl.drawingBufferHeight);
        gl.enable(gl.DEPTH_TEST);

        gl.clearColor(0.0, 0.0, 0.0, 0.0);
        gl.clearDepth(1.0);
        gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

        var space_screen_matrix = mul4(this.viewport.projectionScreenMatrix, this.camera.spaceProjectionMatrix);

        gl.useProgram(this.program);
        gl.uniformMatrix4fv(this.uniform.model_screen_matrix, false, new Float32Array(space_screen_matrix));
        gl.uniform4f(this.uniform.albedo, 0.85, 0.9, 1.0, 1.0);

        gl.enableVertexAttribArray(this.attribute.vertex);
        gl.enableVertexAttribArray(this.attribute.normal);

        gl.bindBuffer(gl.ARRAY_BUFFER, this.buffer);
        gl.vertexAttribPointer(this.attribute.vertex, 3, gl.FLOAT, false, 4 * 6, 4 * 0);
        gl.vertexAttribPointer(this.attribute.normal, 3, gl.FLOAT, false, 4 * 6, 4 * 3);
        gl.drawArrays(gl.TRIANGLES, 0, this.vertices_count);

        gl.uniform4f(this.uniform.albedo, 1.0, 0.8, 0.8, 1.0);

        for (var i = 0; i < this.house.devices.length; i++)
        {
            device = this.house.devices[i];
            device_matrix = space_screen_matrix.slice(0);
            device_matrix[3 * 4 + 0] += device.x * space_screen_matrix[0 *4 + 0] +  device.y * space_screen_matrix[1 *4 + 0] + device.z * space_screen_matrix[2 *4 + 0];
            device_matrix[3 * 4 + 1] += device.x * space_screen_matrix[0 *4 + 1] +  device.y * space_screen_matrix[1 *4 + 1] + device.z * space_screen_matrix[2 *4 + 1];
            device_matrix[3 * 4 + 2] += device.x * space_screen_matrix[0 *4 + 2] +  device.y * space_screen_matrix[1 *4 + 2] + device.z * space_screen_matrix[2 *4 + 2];
            device_matrix[3 * 4 + 3] += device.x * space_screen_matrix[0 *4 + 3] +  device.y * space_screen_matrix[1 *4 + 3] + device.z * space_screen_matrix[2 *4 + 3];
            device_matrix[0 *4 + 0] *= 0.3;
            device_matrix[0 *4 + 1] *= 0.3;
            device_matrix[0 *4 + 2] *= 0.3;
            device_matrix[0 *4 + 3] *= 0.3;
            device_matrix[1 *4 + 0] *= 0.3;
            device_matrix[1 *4 + 1] *= 0.3;
            device_matrix[1 *4 + 2] *= 0.3;
            device_matrix[1 *4 + 3] *= 0.3;
            device_matrix[2 *4 + 0] *= 0.3;
            device_matrix[2 *4 + 1] *= 0.3;
            device_matrix[2 *4 + 2] *= 0.3;
            device_matrix[2 *4 + 3] *= 0.3;

            gl.uniformMatrix4fv(this.uniform.model_screen_matrix, false, new Float32Array(device_matrix));

            gl.bindBuffer(gl.ARRAY_BUFFER, this.cube_buffer);
            gl.vertexAttribPointer(this.attribute.vertex, 3, gl.FLOAT, false, 4 * 6, 4 * 0);
            gl.vertexAttribPointer(this.attribute.normal, 3, gl.FLOAT, false, 4 * 6, 4 * 3);
            gl.drawArrays(gl.TRIANGLES, 0, 36);
        }
    }

    this.load = function()
    {
        var gl = this.gl;

        var vertex_shader_code = [
            "precision mediump float;",
            "attribute vec3 in_vertex;",
            "attribute vec3 in_normal;",
            "varying vec3 normal;",
            "uniform mat4 modelScreenMatrix;",
            "void main() {",
                "normal = in_normal;",
                "gl_Position = modelScreenMatrix * vec4(in_vertex, 1.0);",
            "}"
        ].join("\n");

        var fragment_shader_code = [
            "precision mediump float;",
            "varying vec3 normal;",
            "uniform vec4 albedo;",
            "void main() {",
                "float factor = 0.1 * max(dot(normal, vec3(-3.0, -5.0, 7.0)), 0.0);",
                "gl_FragColor = vec4(1.0, 1.0, 1.0, 1.0) * (0.5 + 0.4 * factor);",
                "gl_FragColor *= albedo;",
                //"gl_FragColor.xyz = 0.5 + 0.5 * normal;",
                "gl_FragColor.a = 1.0;",
            "}"
        ].join("\n");

        var vertex_shader = gl.createShader(gl.VERTEX_SHADER);
        gl.shaderSource(vertex_shader, vertex_shader_code);
        gl.compileShader(vertex_shader);

        var fragment_shader = gl.createShader(gl.FRAGMENT_SHADER);
        gl.shaderSource(fragment_shader, fragment_shader_code);
        gl.compileShader(fragment_shader);

        var program = gl.createProgram();
        gl.attachShader(program, vertex_shader);
        gl.attachShader(program, fragment_shader);
        gl.linkProgram(program);

        this.program = program;

        this.uniform = new Object();
        this.uniform.model_screen_matrix = gl.getUniformLocation(this.program, "modelScreenMatrix");
        this.uniform.albedo = gl.getUniformLocation(this.program, "albedo");

        this.attribute = new Object();
        this.attribute.vertex = gl.getAttribLocation(this.program, "in_vertex");
        this.attribute.normal = gl.getAttribLocation(this.program, "in_normal");

        this.cube_buffer = gl.createBuffer();

        gl.bindBuffer(gl.ARRAY_BUFFER, this.cube_buffer);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(objectsLib.cube), gl.STATIC_DRAW);

    }

    this.load();
    this.update_model();
}

