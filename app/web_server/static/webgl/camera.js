


// model -> view -> projection -> screen

function EngineViewportInit(obj)
{
    obj.width = 512;
    obj.height = 512;

    obj.update = function()
    {
        var scaleRatio = this.width / this.height;

        this.projectionScreenMatrix =
        [
            1.0, 0.0,  0.0,  0.0,
            0.0, scaleRatio,  0.0,  0.0,
            0.0, 0.0,  1.0,  0.0,
            0.0, 0.0,  0.0,  1.0
         ];

        this.screenProjectionMatrix =
        [
            1.0, 0.0,  0.0,  0.0,
            0.0, 1.0 / scaleRatio,  0.0,  0.0,
            0.0, 0.0,  1.0,  0.0,
            0.0, 0.0,  0.0,  1.0
         ];
    }

    obj.update();

}

function EngineCameraInit(obj)
{
    obj.from = [ -1.0, 0.0, 0.0 ];
    obj.at = [ 0.0, 0.0, 0.0 ];
    obj.near = 0.1;
    obj.far = 1000.0;
    obj.angle = Math.PI * 0.5;
    obj.depthTransform = [0.0, 1.0]; // distance = x / (depth + y) ;

    obj.update = function()
    {
        var d = [ this.at[0] - this.from[0], this.at[1] - this.from[1], this.at[2] - this.from[2] ];
        var u = [ d[1], -d[0], 0.0 ];
        var v = cross(u,d);

        d = normalized(d);
        u = normalized(u);
        v = normalized(v);

        var farPlanFactor = this.far / (this.far - this.near);
        var scaleXY = 1.0 / Math.tan (this.angle * 0.5);

        this.depthTransform[0] = -0.5 * this.near * farPlanFactor ;
        this.depthTransform[1] = -farPlanFactor ;

        this.spaceViewMatrix =
        [
            u[0], v[0], d[0], 0.0,
            u[1], v[1], d[1], 0.0,
            u[2], v[2], d[2], 0.0,
            -dot(u,this.from), -dot(v,this.from), -dot(d,this.from), 1.0
         ];

        this.viewSpaceMatrix =
        [
            u[0], u[1], u[2], 0.0,
            v[0], v[1], v[2], 0.0,
            d[0], d[1], d[2], 0.0,
            this.from[0], this.from[1], this.from[2], 1.0
         ];

        this.viewProjectionMatrix =
        [
            scaleXY, 0.0, 0.0, 0.0,
            0.0, scaleXY, 0.0, 0.0,
            0.0, 0.0, farPlanFactor, 1.0,
            0.0, 0.0, -this.near * farPlanFactor, 0.0
         ];

        this.projectionViewMatrix = // should use depthTransform
        [
            1.0 / scaleXY, 0.0, 0.0, 0.0,
            0.0, 1.0 / scaleXY, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 1.0
         ];

        this.spaceProjectionMatrix = mul4(this.viewProjectionMatrix, this.spaceViewMatrix);
        this.projectionSpaceMatrix = mul4(this.viewSpaceMatrix, this.projectionViewMatrix); // should use depthTransform
    }

    obj.update();

}

function Viewport()
{
    EngineViewportInit(this);
}

function Camera()
{
    EngineCameraInit(this);
}

