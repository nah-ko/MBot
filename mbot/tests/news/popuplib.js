<!-- PopUpLIB 0.0 -->
<!-- $Id$ -->
<!-- Original:  Christophe Truffier (toffe@nah-ko.org)  -->
<!-- Web Site:  http://docs.nah-ko.org/docs_perso/popuplib.html  -->
/* ---- How does that works ? ----
You've simply had to make a link in you're web pages like this :
<A HREF="#" ONCLICK="javascript:plopimg('path/to/the/image/to/pop-up'[,'comment']);"><IMG SRC="tiny_image"></A>
If you do not specify a comment, the image name will be used for title.
-------------------------------- */

function plopimg(pathimg,comment)
	{
	if (!comment)
		titlepage = nameimg(pathimg);
	else
		titlepage = comment;
	html = '<html> <head> <title>Image : '+titlepage+'</title> </head> <body onBlur="top.close()" scroll="no" leftmargin="0" marginwidth="0" topmargin="0" marginheight="0"><a href="javascript:window.close()"><IMG src="'+pathimg+'" BORDER=0 NAME=plopimg ALT="Click to close" onLoad="window.resizeTo(document.plopimg.width+10, document.plopimg.height+30)"></a></body></html>';
	popupImage =    window.open('','_blank','toolbar=0, location=0, directories=0, menuBar=0, scrollbars=0, resizable=0');
	popupImage.document.open();
	popupImage.document.write(html);
	popupImage.document.close()
	}; 

/* -------------------------------
This function rename the "file" 
variable even if the path_to is 
very long.
--------------------------------*/
function nameimg(file)
	{
	myRegExp = /(\w*|.{1,})(\/)/g;
	chaine = file;
	newString = chaine.replace(myRegExp, "");
	return newString;
	};

function ploppage(mypage,myname,w,h,pos,infocus)
	{
	var NewPopupWindow=null;

	if(pos=='random') {
		LeftPosition=(screen.width)?Math.floor(Math.random()*(screen.width-w)):100;
		TopPosition=(screen.height)?Math.floor(Math.random()*((screen.height-h)-75)):100;
	}

	if(pos=='center') {
		LeftPosition=(screen.width)?(screen.width-w)/2:100;
		TopPosition=(screen.height)?(screen.height-h)/2:100;
	}
	else if((pos!='center' && pos!='random') || pos==null) {
		LeftPosition=10;
		TopPosition=10;
	}

	settings='width='+ w + ',height='+ h + ',top=' + TopPosition + ',left='+ LeftPosition + ',location=no,directories=no,menubar=no,toolbar=no,status=no,scrollbars=yes,resizable=yes, dependent=no';
	NewPopupWindow=window.open('',myname,settings);

	if(infocus=='front') {
		NewPopupWindow.focus();
		NewPopupWindow.location=mypage;
	}
	};
