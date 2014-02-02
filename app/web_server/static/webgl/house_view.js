
function HouseRect(x, y, w, h)
{
    this.x = x;
    this.y = y;
    this.w = w;
    this.h = h;
}

function House()
{
    this.rooms = new Array();

    this.addRoom = function(x, y, w, h)
    {
        this.rooms.push(new HouseRect(x, y, w, h))
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

function HouseWall(house)
{
    this.walls = new Array();



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

        this.update()
    }

    this.draw = function()
    {
        var gl = this.gl;

        gl.clearColor(0.2, 0.5, 1.0, 1.0);
        gl.clear(gl.COLOR_BUFFER_BIT);

        var model_screen_matrix = mul4(this.viewport.projectionScreenMatrix, this.camera.modelProjectionMatrix);

        gl.useProgram(self.program);
        gl.uniformMatrix4fv(self.uniform.model_screen_matrix, false, new Float32Array(model_screen_matrix));

    }

    this.load = function()
    {
        var gl = this.gl;

        var vertex_shader_code = [
            "attribute vec3 vertex;",
            "uniform mat4 modelScreenMatrix;",
            "void main() {",
                "gl_Position = modelScreenMatrix * vec4(vertex, 1.0);",
            "}"
        ].join("\n");

        var fragment_shader_code = [
            "void main() {",
                "gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);",
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

        this.attribute = new Object();
        this.attribute.vertex = gl.getAttribLocation(this.program, "vertex");
    }

    this.load();
    this.update_model();
}

