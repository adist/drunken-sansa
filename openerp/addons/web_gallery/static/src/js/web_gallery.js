(function(window) {

function Gallery(grid, type) {
	this.grid = grid;
	this.gridWidth = $('ul.notebook-tabs-strip').width() - 70;
	this.type = type;
	this.viewport = null;
};

var PAGE_WIDTH = 120;

var CAROUSEL_BUTTON_WIDTH = 36;

Gallery.prototype.resizeViewport = function() {
	this.viewport.width(Math.floor((this.gridWidth
		- CAROUSEL_BUTTON_WIDTH * 2)
		/ PAGE_WIDTH) * PAGE_WIDTH);
	
};

Gallery.prototype.constructCategoryLayout = function(allContainer, cat, elementArray) {
	
	allContainer.append($("<h3/>").text(cat));
	
	var slider = $('<div class="slider-code"></div>');
	this.viewport = $('<div class="viewport"></div>');
	var ul = $('<div class="overview"></div>');
	
	for (var i = 0; i < elementArray.length; i++) {
		var li = $('<div/>');
		var element = elementArray[i];
		element.width(PAGE_WIDTH);
		ul.append(li.append(element));
	};
	this.viewport.append(ul);
	
	slider.append('<a class="buttons prev" href="#"></a>')
		.append(this.viewport)
		.append('<a class="buttons next" href="#"></a>');
		
	allContainer.append(slider);
	this.resizeViewport();
};

Gallery.prototype.append_category_containers = function(element, all_container, type) {
	
	var cats = {};
	
	element.find("span[name=url]").each(function() {
		var $this = $(this),
		$tr = $this.parents('tr:first'),
		category = $tr.find('td span[name=category]').html();
		
		if (category === '') {
			category = "Uncategorized";
		};
		
		if (typeof cats[category] === 'undefined')
			cats[category] = [];
		cats[category].push($this);
	});
	
	for (cat in cats) {
		//do cat h3
		var elementArray = [];
		for (var i=0, l=cats[cat].length; i<l; i++) {
			var $this = cats[cat][i],
			$tr = $this.parents('tr:first'),
			
			edit = $tr.find('td:first > img').clone(),
			del = $tr.find('td:last > img').clone(),
			comment = $tr.find('td span[name=comment]').html();
			
			edit.css({'top':'1px', 'left':'80px', 'position':'absolute'});
			del.css({'top':'1px', 'left':'100px', 'position':'absolute'});
			var image_url, video_url, doc_url;
			image_url = video_url = doc_url = $this.text();
			
			if (type == "video") {
				image_url = '/web_gallery/static/img/player.jpg';
			}
			
			var image = $("<img />")
							.attr("src", image_url)
							.attr("width", 100)
							.attr("style", "padding: 10px");
			
			if (type == "doc") {
				var doc_ext = doc_url.substr(-3);
				var EXTENTIONS = {'xls':'xls', 'pdf':'pdf', 'doc':'doc'};
				
				image.attr('src', "/web_gallery/static/img/" +
					EXTENTIONS[doc_ext] +".png");
			}
			
			var link = $("<a />");
			
			switch (type) {
				case "image":
					link
					.addClass("fancybox_image_gallery")
					.attr("href", image_url)
					.attr("target", "_self")
					.attr("rel", "fancybox_image_gallery")
					.attr("title", comment);
				break;
				case "video":
					link
					.addClass("fancybox_video_gallery")
					.attr("video", video_url)
					.attr("href", "#fancy_video")
					.attr("target", "_self")
					.attr("rel", "fancybox_video_gallery")
					.attr("title", comment);
				break;
				case "doc":
					link
					.attr("href", doc_url)
					.attr("target", "_blank")
					.attr("title", comment);
				break;
			};
			link.append(image);
				var spn = $('<div style="position:relative;"></div>').append(edit).append(del).append(link);
			elementArray.push(spn);
		};
		this.constructCategoryLayout(all_container, cat, elementArray);
	}
};

Gallery.prototype.append_comment = function(container, comment) {
	container.css({"vertical-align": "top"});
	container.append("<br />");
	container.append($("<span />")
		.css({"width": "100px", "display":"inline-block"})
		.text(comment));
};


Gallery.prototype.setGallery = function() {
	var grid = this.grid;
	var type = this.type;
	
	var table = grid.parents("table:first");
	
	$('.' + type + '_grid_container').remove();
	var grid_container = $('<div class="' + type + '_grid_container"></div>');
	grid_container.insertAfter(table);
	
	this.append_category_containers(grid, grid_container, type);
	
	$("a.fancybox_image_gallery").fancybox({});
	$(".fancybox_video_gallery").fancybox({
		'padding': 0,
		'autoScale': false,
		'transitionIn': 'none',
		'transitionOut': 'none',
		'autoDimensions': false,
		'width': 640,
		'height': 480
	})
		.click(function() {
			$.fancybox({
				'type': 'inline',
				'autoDimensions': false,
				'width': 640,
				'height': 480
			});
			$('#fancybox-inner').append('<div id="fancy_video">Video is loading...</div>');
			var file_link = $(this).attr('video');
			jwplayer("fancy_video").setup({
				flashplayer: "/web_gallery/static/img/player.swf",
				file: file_link,
				autoplay: true,
				height: 475,
				width: 635
			});
		return false;
	});
	$('.slider-code').each(function() {
		$(this).tinycarousel({display:1, pageWidth:PAGE_WIDTH});
	});
	
	if ($("[id=" + table.attr('id') + "_btn_]").length == 1) {
		var buttonWrapper = $('<div style="padding:10px"></div>');
		var btn = $("[id=" + table.attr('id') + "_btn_]").clone();
		table.before(buttonWrapper.append(btn));
	}
	grid_container.width(this.gridWidth);
	table.hide();
};

Gallery.setUp = function() {
	var types = ['image', 'video', 'doc'], grid, sel;
	var itsGallery = false;
	if (!Gallery.currentType) {
		for (var i=0; i < types.length; i++) {
			sel = "table[id*=web_gallery_" + types[i] + "_ids_grid]";
			grid = $(sel);
			if (!grid.length)
				continue;
			new Gallery(grid, types[i]).setGallery();
		}
	} else {
		sel = "table[id*=web_gallery_" + Gallery.currentType + "_ids_grid]";
		grid = $(sel);
		new Gallery(grid, Gallery.currentType).setGallery();
	}
	itsGallery = true;
	return itsGallery;
};


// init gallery
var galleryInit = function() {
	var parentUl = $('.notebook-tabs ul');
	if (parentUl.hasClass('galleryLoaded') || !Gallery.setUp())
		return;
	parentUl.addClass("galleryLoaded");
		
	$("body").ajaxComplete(function(event, ajaxRequest, options) {
		if (options["url"] == "/openerp/listgrid/get") {
			setTimeout(function() {
			$('.ui-dialog').remove();
			Gallery.setUp();
				}, 400);
		};
	});
};

window.Notebook.prototype.__wrapp_init = window.Notebook.prototype.__init__;
window.Notebook.prototype.__init__ = function(el, opts) {
	this.__wrapp_init(el, opts);
	galleryInit();
};

})(window);
