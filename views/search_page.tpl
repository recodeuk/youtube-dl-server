<link href="//maxcdn.bootstrapcdn.com/bootstrap/4.1.1/css/bootstrap.min.css" rel="stylesheet" id="bootstrap-css">
<script src="//maxcdn.bootstrapcdn.com/bootstrap/4.1.1/js/bootstrap.min.js"></script>
<script src="//cdnjs.cloudflare.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
<!------ Include the above in your HEAD tag ---------->
<head><script>

	% for i in button_code:
		var myFunction{{i[0]}} = function () {
                 var Url = window.location;
                 fetch(Url["origin"] + "/youtube-dl/q",{body:new URLSearchParams({url:"{{i[1]}}",format:"{{i[2]}}"}),method:"POST"});};
    % end


</script></head>
<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.2.0/css/all.css" integrity="sha384-hWVjflwFxL6sNzntih27bfxkr27PmbbK/iSvJ+a4+0owXq79v+lsFkW54bOGbiDQ" crossorigin="anonymous">
<div class="container">
    <br>
    <div class="container-fluid">
    <div class="row">
    	% for c in cards:
		<div class="col-md-4">
	         <div class="card mb-4">
	            <img class="card-img-top" src="{{c[0]}}}" alt="Card image cap">
	            <div class="card-body">
	               <h5 class="card-title">{{c[1]}}</h5>
	               <a onclick="myFunction{{c[2]}}()" class="btn btn-outline-dark btn-sm">Download</a>
	            </div>
	         </div>
	      </div>
	    % end
	    </div>
	</div>
</div>