

function EngineConsole()
{
    this.track = true;
    this.status = 'ok';

    this.constructConsole = function()
    {
        if (document.getElementById('consoleOutput'))
        {
            return true;
        }

        var div = document.createElement('div');

        div.setAttribute('id', 'consoleOutput');
        div.style.position = 'absolute';
        div.style.top = '0px';
        div.style.left = '0px';
        div.style.width = utilWindowWidth() + 'px';
        div.style.height = utilWindowHeight() + 'px';
        div.style.background = 'rgba(0,0,0,0.6)';
        div.style.color = 'rgba(255,255,255,0.5)';
        div.style.zIndex = '1';
        div.style.fontFamily = 'Consolas, monospace';
        div.style.display = 'none';
        div.style.overflow = 'scroll';

        document.body.appendChild(div);

        return true;
    }

    this.show = function()
    {
        document.getElementById('consoleOutput').style.display = 'block';
    }

    this.hide = function()
    {
        if (this.status != 'ok')
        {
            return;
        }

        document.getElementById('consoleOutput').style.display = 'none';
    }

    this.print = function(message, type)
    {
        var html = '';

        if (type == 'error')
        {
            html += ' style="color:#DD0000;"';
        }

        var messageLines = message.split('\n');

        message = messageLines.join('</div><div' + html + '>');

        document.getElementById('consoleOutput').innerHTML += '<div' + html + '>' + message + '</div>';
    }

    this.tracking = function(message)
    {
        if (this.track)
        {
            this.print('tracking: ' + message, 'tracking')
        }
    }

    this.trackingMatrix = function(message, matrix)
    {
        var html = '<div>' + message + '</div>';

        html += '<table style="color:#FFFFFF;">';
        html += '<tr><td>' + matrix[0 + 4 * 0] + '</td><td>' + matrix[0 + 4 * 1] + '</td><td>' + matrix[0 + 4 * 2] + '</td><td>' + matrix[0 + 4 * 3] + '</td></tr>';
        html += '<tr><td>' + matrix[1 + 4 * 0] + '</td><td>' + matrix[1 + 4 * 1] + '</td><td>' + matrix[1 + 4 * 2] + '</td><td>' + matrix[1 + 4 * 3] + '</td></tr>';
        html += '<tr><td>' + matrix[2 + 4 * 0] + '</td><td>' + matrix[2 + 4 * 1] + '</td><td>' + matrix[2 + 4 * 2] + '</td><td>' + matrix[2 + 4 * 3] + '</td></tr>';
        html += '<tr><td>' + matrix[3 + 4 * 0] + '</td><td>' + matrix[3 + 4 * 1] + '</td><td>' + matrix[3 + 4 * 2] + '</td><td>' + matrix[3 + 4 * 3] + '</td></tr>';
        html += '</table>';

        document.getElementById('consoleOutput').innerHTML += html;
    }

    this.error = function(message)
    {
        this.status = 'error';
        this.show();

        this.print('ERROR: ' + message, 'error')
    }

    this.constructConsole();

}









