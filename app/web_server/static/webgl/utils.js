

// --------------------------------------------------------------- COMPATIBILITY

function utilWindowWidth()
{
    return  window.innerWidth || document.documentElement.clientWidth || d.getElementsByTagName('body')[0].clientWidth;
}

function utilWindowHeight()
{
    return  window.innerHeight || document.documentElement.clientHeight || d.getElementsByTagName('body')[0].clientHeight;
}

function utilLoadFile(url)
{
    if (window.XMLHttpRequest)
    {// code for IE7+, Firefox, Chrome, Opera, Safari
        xmlhttp = new XMLHttpRequest();
    }
    else
    {// code for IE6, IE5
        xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
    }

    xmlhttp.open("GET", url, false);
    xmlhttp.send();

    return xmlhttp.responseXML;
}

function utilParseXml(url)
{
    if (window.XMLHttpRequest)
    {// code for IE7+, Firefox, Chrome, Opera, Safari
        xmlhttp = new XMLHttpRequest();
    }
    else
    {// code for IE6, IE5
        xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
    }

    xmlhttp.open("GET", url, false);
    xmlhttp.send();

    return xmlhttp.responseXML;
}

function utilDirName(url)
{
    return url.replace(/\\/g, '/').replace(/\/[^\/]*\/?$/, '') + '/';
}

function utilBaseName(url)
{
    return url.replace(/\\/g,'/').replace( /.*\//, '' );
}

function createWebGLXContext(canvas,version)
{
    var gl = null;

    if (version == undefined)
    {
        version = 1;
    }

    if (version == 2)
    {
        gl = canvas.getContext("experimental-webgl2");

        if (!gl)
        {
            throw 'WebGL 2 unsupported';
        }

        if (!gl instanceof WebGL2RenderingContext)
        {
            // unexpected rendering context.
            return false;
            throw 'Unexpected WebGL 2 rendering context';
        }
    }
    else if (version == 1)
    {
        gl = canvas.getContext("experimental-webgl");

        if (!gl)
        {
            throw 'WebGL 1 unsupported';
        }

        if (!gl instanceof WebGLRenderingContext)
        {
            throw 'Unexpected WebGL 1 rendering context';
        }
    }

    return gl;
};


// --------------------------------------------------------------- MATH

function cross(a,b)
{
    return [ a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0] ];
}

function normalized(a)
{
    var l = 1.0 / Math.sqrt( a[0] * a[0] + a[1] * a[1] + a[2] * a[2] );

    return [ a[0] * l, a[1] * l, a[2] * l ];
}

function setNorme(a,n)
{
    var l = n / Math.sqrt( a[0] * a[0] + a[1] * a[1] + a[2] * a[2] );

    return [ a[0] * l, a[1] * l, a[2] * l ];
}

function dot(a,b)
{
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
}

function lookAtMatrix(from, at, minDistance, maxDistance)
{
    var d = [ at[0] - from[0], at[1] - from[1], at[2] - from[2] ];
    var u = [ d[1], -d[0], 0.0 ];
    var v = cross(u,d);

    d = setNorme(d,1.0/(maxDistance-minDistance));
    u = normalized(u);
    v = normalized(v);

    var m = [ u[0], v[0], d[0], 0.0,
             u[1], v[1], d[1], 0.0,
             u[2], v[2], d[2], 0.0,
             -dot(u,from), -dot(v,from), -dot(d,from), 1.0 ];

    return m;
}

function viewportMatrix(width,height)
{
    var scaleRatio = width / height;

    return [ 1.0, 0.0,  0.0,  0.0,
            0.0, scaleRatio,  0.0,  0.0,
            0.0, 0.0,  1.0,  0.0,
            0.0, 0.0,  0.0,  1.0 ];
}

function mat4identity(scaleFactor)
{
    return [ scaleFactor, 0.0,  0.0,  0.0,
            0.0, scaleFactor,  0.0,  0.0,
            0.0, 0.0,  scaleFactor,  0.0,
            0.0, 0.0,  0.0,  1.0 ];
}

function matDot(a,b,an,bn)
{
    return ( a[an+0] * b[4*bn+0] + a[an+4] * b[4*bn+1] + a[an+8] * b[4*bn+2] + a[an+12] * b[4*bn+3] );
}

function mul4(a,b)
{
    return [
            matDot(a,b, 0, 0), matDot(a,b, 1, 0), matDot(a,b, 2, 0), matDot(a,b, 3, 0),
            matDot(a,b, 0, 1), matDot(a,b, 1, 1), matDot(a,b, 2, 1), matDot(a,b, 3, 1),
            matDot(a,b, 0, 2), matDot(a,b, 1, 2), matDot(a,b, 2, 2), matDot(a,b, 3, 2),
            matDot(a,b, 0, 3), matDot(a,b, 1, 3), matDot(a,b, 2, 3), matDot(a,b, 3, 3)
            ];
}

function floatReste(a, b)
{
    return a - b * Math.floor(a / b);
}




