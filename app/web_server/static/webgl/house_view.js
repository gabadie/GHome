
function House()
{

}

function HouseView(output, canvas_id, house)
{
    this.output = output;
    this.canvas = document.getElementById(canvas_id);

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

    this.draw = function()
    {
        gl = this.gl;

        gl.clearColor(0.2, 0.5, 1.0, 1.0);
        gl.clear(gl.COLOR_BUFFER_BIT);
    }

    this.update()

}

