from app import app

@app.route('/global_testing')
def global_testing():
    res = """<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" HREF="javascript:alert('XSS');">
        <meta charset="utf-8" />
        <title>Flask Test</title>
    </head>

    <body>
    <a href=/test_link_list> path to link list </a>
    <a href=/regular_tag_content> path to regular tag content </a>
    <a href=/link_tag_content> path to link tag content </a>
    <a href=/inline_style> path to regular tag content </a>

    
        <h1 style= display:block>Compiled flask test</h1>
        <img src=a onerror="javascript:console.log('lol')"></img>

        <img src=http://test.com/simple/1></img>
        <img src=http://test.com/simple/2></img>
        <img src=http://test.com/simple/3></img>
        <img src=http://test.com/simple/4></img>
        <img src=http://test.com/simple/5></img>
        
        <div onclick=event></div>

    <script>
        var web_socket_variable = "http://not-example.com/";
        var blockedWorker = new Worker("data:application/javascript");
        navigator.serviceWorker.register('https://not-example.com/sw.js');

        var xhr = new XMLHttpRequest();
        xhr.open('GET', 'https://not-example.com/');
        xhr.send();

        myStyle.insertRule('#blanc { color: white }', 0);

        eval('2*3');

        console.log('var i = 53;');

        var ws = new WebSocket(web_socket_variable);
        var es = new EventSource("https://not-example.com/");
   </script>

   <style> test style </style>

    <script>
        var ws = new WebSocket("http://secondscript.com/");
        var es = new EventSource("https://secondscript.com/");
		myStyle.insertRule('#blanc { color: white }', 0);
		document.getElementByTagName(body).style.cssText = "background-color:pink;";
    </script>

    <a href=/target> follow </a>

    </body>

</html>
    """
    return res

@app.route('/')
def index():
    res = """<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8" />
        <title>Flask Link test</title>
    </head>
    
    <body>
        <a href=/target> follow </a>
        <a href=//google.com> google </a>
    </body>
    
</html>
    """
    return res

@app.route('/test_link_list')
def test_link_list():
    res = """<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8" />
        <title>Flask Link test</title>
    </head>
    
    <body>
        <a href=/d1> D1 </a>
        <a href=/d2> D2 </a>
    </body>
    
</html>
    """
    return res

@app.route('/d1')
def d1():
    res = """<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8" />
        <title>Flask Link test</title>
    </head>
    
    <body>
        <a href=/d3> D3 </a>
        <a href=/d4> D4 </a>
    </body>
    
</html>
    """
    return res

@app.route('/d2')
def d2():
    res = """<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8" />
        <title>Flask Link test</title>
    </head>
    
    <body>
        <a href=/d5> D5 </a>
        <a href=/not_exist> This link does not exist and should not appear anywhere </a>
    </body>
    """
    return res


@app.route('/d3')
def d3():
    res = """<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8" />
        <title>Flask Link test</title>
    </head>
    
    <body>
        <h1> Dead end for links that should appear </h1>
        <a href=https://not-example.com> Link not to follow </a>
    </body>
    """
    return res


@app.route('/d4')
def d4():
    res = """<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8" />
        <title>Flask Link test</title>
    </head>
    
    <body>
        <a href=/d6> D6 </a>
        <h1> Dead end for links that should appear </h1>
    </body>
    """
    return res


@app.route('/d5')
def d5():
    res = """<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8" />
        <title>Flask Link test</title>
    </head>
    
    <body>
        <a href=/d7> D7 </a>
        <a href=https://not-example.com> Link not to follow </a>
        <a href=/d9> D9 </a>
    </body>
    """
    return res

@app.route('/d6')
def d6():
    res = """<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8" />
        <title>Flask Link test</title>
    </head>
    
    <body>
        <a href=https://not-example.com> Link not to follow </a>
        <a href=/d8> D8 </a>
    </body>
    """
    return res

@app.route('/d7')
def d7():
    res = """<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8" />
        <title>Flask Link test</title>
    </head>
    
    <body>
        <a href=/d8> D8 </a>
    </body>
    """
    return res

@app.route('/d8')
def d8():
    res = """<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8" />
        <title>Flask Link test</title>
    </head>
    
    <body>
        <h1> End for d8 </h1>
        <a href=https://google.com> Link not to follow </a>
    </body>
    """
    return res


@app.route('/d9')
def d9():
    res = """<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8" />
        <title>Flask Link test</title>
    </head>
    
    <body>
        <h1> End for d9 </h1>
        
    </body>
    """
    return res

@app.route('/regular_tag_content')
def regular_tag_content():
    res = """<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8" />
        <title>Flask Link tag sorting test</title>
    </head>
    
    <body>
        <img src="img.gif" alt="Smiley face" height="42" width="42"> 
        
        <audio controls>
            <source src="audio1.ogg" type="audio/ogg">
            <source src="/audio/audio2.mp3" type="audio/mpeg">
            Your browser does not support the audio element.
        </audio> 
        
        <video src="/video/pass-countdown.ogg" width="170" height="85" controls>
            <p>If you are reading this, it is because your browser does not support the HTML5 video element.</p>
        </video>
        
        <audio src="http://mysuperaudioresourcesite.com/awesomesound.ogg">
            <track kind="captions" src="/media/track1.vtt" srclang="en" label="English">
            <track kind="captions" src="/media/track2.vtt" srclang="sv" label="Svenska">
        </audio>
        
        <embed src="embed.swf"> 
        
        <applet code="applet.class" width="350" height="350">
            Java applet that draws animated bubbles.
        </applet> 
        
        <form action="http://evil_test.fr">
            First name:<br>
            <input type="text" name="firstname" value="Mickey"><br>
            Last name:<br>
            <input type="text" name="lastname" value="Mouse"><br><br>
            <input type="submit" value="Submit">
        </form> 
        
        <frame name="main" src="http://frame.access" /> 
        <iframe name="main" src="http://frame.access" /> 
    
</html>
    """
    return res


@app.route('/link_tag_content')
def link_tag_content():
    res = """<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8" />
        <title>Flask Link tag sorting test</title>
    </head>
    
    <body>
        <link rel="assets" href="test.js">
        <link rel="icon" href="/favicon">
        
        <link rel="stylesheet" href="media/examples/link-element-example.css">
        
        <link rel="prefetch" href="/style.css" as="style" />
        <link rel="preload" href="/preload.css" as="style" />
        
        <link rel="manifest" href="manifest.css" as="style" />
        <link rel="manifest" href="/preload.css" as="style" />
        
        <link rel="dns-prefetch" href="dns-prefetch.dns">
    </body>
    
</html>
    """
    return res

@app.route('/inline_directive_nonce')
def inline_directive_nonce():
    res = """<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8" />
        <title>Flask Link tag sorting test</title>
    </head>
    
    <body>
        <script nonce="EDNnf03nceIOfn39fn3e9h3sdfa"> 
            var test = 'first script';
            console.log(test);
        </script>
        
        <script nonce="AmnjUXEBF5jf1EKGnkubMhHzZo4"> 
            var test = 'second script";
            console.log(test);
        </script>
    </body>
    
</html>
    """
    return res

@app.route('/inline_directive')
def inline_directive():
    res = """<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8" />
        <title>Flask Link tag sorting test</title>
    </head>
    
    <body>
        
        <p onclick="console.log('test');">
            I'm a paragraph that alert onclick 
        </p>
        
        <p style="color:blue;font-size:46px;">
            I'm a big, blue, <strong>strong</strong> paragraph
        </p>
        
    </body>
    
</html>
    """
    return res

@app.route('/inline_directive_oneliner')
def inline_directive_oneliner():
    res = """<!DOCTYPE html> <html> <head> <meta charset="utf-8" /> <title>Flask Link tag sorting test</title> </head> <body> <p onclick="console.log('test');"> I'm a paragraph that alert onclick </p> <p style="color:blue;font-size:46px;"> I'm a big, blue, <strong>strong</strong> paragraph </p> </body> </html>"""
    return res


@app.route('/sandbox_directive')
def sandbox_directive():
    res = """<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8" />
        <title>Flask Link tag sorting test</title>
    </head>
    
    <body>
        <iframe src="demo_iframe_sandbox.htm" sandbox='allow-same-origin allow-scripts allow-top-navigation'></iframe>
    </body>
    
</html>
    """
    return res


@app.route('/nested_variable')
def nested_variable():
    res = """
    <!DOCTYPE html>
    <html>

    <head>
    <meta charset="utf-8" />
    <title>CSP PoC</title>
    </head>

    <body>
    <script>
        var n1 = 'http://localhost:4000/nest_connect_xmlhttp';
        var n2 = n1;
        
        var n5 = 'http://localhost:4000/nest_connect_socket';
        var n6 = n5;
        var n7 = n6;
        var n8 = n7;

        var xhr = new XMLHttpRequest();
        xhr.open('GET', n2);
        
        var socket = new WebSocket(n7, test);
        xhr.send()

        blockedworker = new SharedWorker(n3);
        
    </script>
    </body>
    </html>
    """
    return res

@app.route('/extract_inline_source_script')
def extract_inline_source_script():
    res = """
    <!DOCTYPE html>
    <html>

    <head>
    <meta charset="utf-8" />
    <title>CSP PoC</title>
    </head>
    <body>
    
    <script>
    </script>
    
    <script>
    </script>
    
    </body>
    </html>
    """
    return res


@app.route('/inline_style')
def inline_style():
    res = """
    <!DOCTYPE html>
    
    <html>

    <head>
    <meta charset="utf-8" />
    <title>CSP PoC</title>
    </head>
    <body>
    <p>test</p>
    <style>
        @font-face {
          font-family: 'PT Serif';
          font-style: normal;
          font-weight: normal;
          src: url('http://myfontsite.font') format('woff'); 
          }
          
        @font-face {
          font-family: 'PT Serif';
          font-style: normal;
          font-weight: normal;
          src: url('https://otherfontsite.lu') format('woff'); 
          }
         
         @import "relative.css";
         @import url('url.css');
         
    </style>
    
    </body>
    </html>
    """
    return res
