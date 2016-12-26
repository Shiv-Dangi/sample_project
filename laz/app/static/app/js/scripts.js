!function(a){"use strict";"function"!=typeof String.prototype.trim&&(String.prototype.trim=function(){return this.replace(/^\s+|\s+$/g,"")}),a.fn.uouAccordion=function(){var b=a(this),c=b.find(".accordion-item");return c.find(".accordion-item-content:visible").css("display","block"),c.find(".accordion-item-content:hidden").css("display","none"),c.find(".accordion-toggle").each(function(){a(this).click(function(){b.hasClass("type-toggle")||(b.find(".accordion-item.active .accordion-toggle .fa-minus").removeClass("fa-minus").addClass("fa-plus"),b.find(".accordion-item.active .accordion-item-content").slideUp(300),b.find(".accordion-item").removeClass("active")),a(this).find(".fa").toggleClass("fa-plus fa-minus"),a(this).parents(".accordion-item").toggleClass("active").find(".accordion-item-content").slideToggle(300,function(){a(this).is(":visible")?a(this).css("display","block"):a(this).css("display","none")})})}),!1},a.fn.uouAlertMessage=function(){var b=a(this),c=b.find(".close");c.click(function(){b.slideUp(300)})},a.fn.uouContactForm=function(){var b="form"===a(this).prop("tagName").toLowerCase()?a(this):a(this).find("form"),c=b.find(".submit-btn");b.submit(function(d){if(d.preventDefault(),!c.hasClass("loading")){if(!b.uouFormValid())return b.find("p.alert-message.warning.validation").slideDown(300),!1;c.addClass("loading").attr("data-label",c.text()),c.text(c.data("loading-label")),a.ajax({type:"POST",url:b.attr("action"),data:b.serialize(),success:function(d){b.find(".alert-message.validation").hide(),b.prepend(d),b.find(".alert-message.success, .alert-message.phpvalidation").slideDown(300),c.removeClass("loading"),c.text(c.attr("data-label")),d.indexOf("success")>0&&b.find("input, textarea").each(function(){a(this).val("")})},error:function(){b.find(".alert-message.validation").slideUp(300),b.find(".alert-message.request").slideDown(300),c.removeClass("loading"),c.text(c.attr("data-label"))}})}})},a.fn.uouCheckboxInput=function(){var b=a(this),c=b.find("input");c.is(":checked")?b.addClass("active"):b.removeClass("active"),c.change(function(){c.is(":checked")?b.addClass("active"):b.removeClass("active")})},a.fn.uouRadioInput=function(){var b=a(this),c=b.find("input"),d=c.attr("name");c.is(":checked")&&b.addClass("active"),c.change(function(){d&&a('.radio-input input[name="'+d+'"]').parent().removeClass("active"),c.is(":checked")&&b.addClass("active")})},a.fn.uouSelectBox=function(){var c=a(this),d=c.find("select");c.prepend('<ul class="select-clone custom-list"></ul>');var e=d.data("placeholder")?d.data("placeholder"):d.find("option:eq(0)").text(),f=c.find(".select-clone");c.prepend('<input class="value-holder" type="text" disabled="disabled" placeholder="'+e+'"><i class="fa fa-chevron-down"></i>');var g=c.find(".value-holder");a.fn.placeholder&&c.find("input, textarea").placeholder(),d.find("option").each(function(){a(this).attr("value")&&f.append('<li data-value="'+a(this).val()+'">'+a(this).text()+"</li>")}),c.click(function(){var a=b();a>991&&(f.slideToggle(100),c.toggleClass("active"))}),f.find("li").click(function(){g.val(a(this).text()),d.find('option[value="'+a(this).attr("data-value")+'"]').attr("selected","selected"),c.hasClass("links")&&(window.location.href=d.val())}),c.bind("clickoutside",function(a){f.slideUp(100)}),c.hasClass("links")&&d.change(function(){window.location.href=d.val()})},a.fn.uouFormValid=function(){function b(a){var b=/^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;return b.test(a)}var c=a(this),d=!0;return c.find("input.required, textarea.required, select.required").each(function(){var c=a(this),e=c.val(),f=!1;""!==e.trim()?c.hasClass("email")?b(e)?(c.removeClass("error"),f=!0):c.addClass("error"):"select"===c.prop("tagName").toLowerCase()&&(null===e||e===c.data("placeholder"))?(c.addClass("error"),c.parents(".select-box").addClass("error")):(c.removeClass("error"),f=!0):c.addClass("error"),d=!!f&&d}),d},a.fn.uouImagesLoaded=function(b){if(a.isFunction(b)){var c=a(this).find("img"),d=0,e=c.length;e>0?c.one("load",function(){d++,d===e&&b.call()}).each(function(){this.complete&&a(this).load()}):b.call()}},a.fn.uouInitLightboxes=function(){a.fn.magnificPopup&&a(this).find("a.lightbox").each(function(){var b=a(this),c=!!b.data("lightbox-group")&&b.data("lightbox-group");c?a('a.lightbox[data-lightbox-group="'+c+'"]').magnificPopup({type:"image",removalDelay:300,mainClass:"mfp-fade",gallery:{enabled:!0}}):b.magnificPopup({type:"image"})})};var b=function(){a("#media-query-breakpoint").length<1&&a("body").append('<var id="media-query-breakpoint"><span></span></var>');var b=a("#media-query-breakpoint").css("content");return"undefined"!=typeof b?(b=b.replace('"',"").replace('"',"").replace("'","").replace("'",""),isNaN(parseInt(b,10))&&(a("#media-query-breakpoint span").each(function(){b=window.getComputedStyle(this,":before").content}),b=b.replace('"',"").replace('"',"").replace("'","").replace("'","")),isNaN(parseInt(b,10))&&(b=1199)):b=1199,b};a.fn.uouToggle=function(){var b=a(this),c=b.find(".toggle-title"),d=b.find(".toggle-content");c.click(function(){b.toggleClass("closed"),d.slideToggle(200)})},a.fn.uouTwitterFeed=function(){if(a.fn.tweet){var b=a(this),c=b.data("id"),d=b.data("limit"),e=b.parents(".twitter-widget");b.bind("loaded",function(){if(e.removeClass("loading"),b.hasClass("paginated")&&a.fn.owlCarousel){var c=!!b.data("interval")&&parseInt(b.data("interval"))>0;b.find(".tweet-list").fadeIn(500),e.find(".tweet-nav").fadeIn(500),b.find(".tweet-list").owlCarousel({autoPlay:c,slideSpeed:300,pagination:!1,paginationSpeed:400,singleItem:!0}),e.find(".tweet-nav-prev").click(function(){b.find(".tweet-list").trigger("owl.prev")}),e.find(".tweet-nav-next").click(function(){b.find(".tweet-list").trigger("owl.next")})}}),b.tweet({username:c,modpath:"./library/twitter/",count:d,loading_text:'<span class="loading-anim"><span></span></span>'})}},a(document).ready(function(){var c=b();if(a.fn.placeholder&&a("input, textarea").placeholder(),a(".accordion-container").each(function(){a(this).uouAccordion()}),a(".alert-message").each(function(){a(this).uouAlertMessage()}),a(".checkbox-input").each(function(){a(this).uouCheckboxInput()}),a(".radio-input").each(function(){a(this).uouRadioInput()}),a(".select-box").each(function(){a(this).uouSelectBox()}),a(".calendar-input").each(function(){var b=a(this).find("input"),c=b.data("dateformat")?b.data("dateformat"):"m/d/y",d=a(this).find(".fa"),e=b.datepicker("widget");b.datepicker({dateFormat:c,minDate:0,beforeShow:function(){b.addClass("active")},onClose:function(){b.removeClass("active"),e.hide(),e.parent().is("body")||e.detach().appendTo(a("body"))}}),d.click(function(){b.focus()})}),a("body").uouInitLightboxes(),a(".progress-bar").each(function(){a(this).uouProgressBar()}),a(".radial-progress-bar").each(function(){a(this).uouRadialProgressBar()}),a(".tabs-container").each(function(){a(this).uouTabbed()}),a(".toggle-container").each(function(){a(this).uouToggle()}),a(".header-search").each(function(){var b=a(this),d=b.find(".search-input input"),e=b.find(".search-advanced");d.focus(function(){b.addClass("active"),a(this).addClass("active"),a(this).parent().find(".ico").fadeOut(300),e.slideDown(200)}),b.bind("clickoutside",function(f){if(c>991){var g=a(f.target);g.hasClass("ui-datepicker-prev")||g.hasClass("ui-datepicker-next")||(d.blur(),b.removeClass("active"),d.removeClass("active"),""===d.val()&&d.parent().find(".ico").fadeIn(300),e.slideUp(200),b.find(".select-box .select-clone").slideUp(200))}}),b.find(".calendar-input").each(function(){var b=a(this),c=b.find("input").datepicker("widget");b.find("input").focus(function(){c.detach().insertAfter(b.parent())})})}),a(".banner-search-inner").each(function(){var b=a(this),c=b.find(".tab-title"),d=b.find(".tab-content");c.click(function(){if(!a(this).hasClass("active")){var b=a(this).index();c.filter(".active").removeClass("active"),a(this).addClass("active"),d.filter(".active").hide().removeClass("active"),d.filter(":eq("+b+")").show().addClass("active"),a.fn.owlCarousel&&a("#banner .banner-bg").trigger("owl.goTo",b)}})}),a("#contact-form").each(function(){a(this).uouContactForm()}),a(".properties-search-type").each(function(){var b=a(this),c=b.find("input[type=radio]");c.each(function(){a(this).change(function(){a("#properties-search-form-swap, #properties-search-form-book, #properties-search-form-rent").hide(),a("#properties-search-form-"+a(this).data("type")).show()})})}),a(".properties-search-filter .price-filter .slider-range-container").each(function(){if(a.fn.slider){var b=a(this),c=b.find(".slider-range"),d=c.data("min")?c.data("min"):100,e=c.data("max")?c.data("max"):2e3,f=c.data("step")?c.data("step"):100,g=c.data("default-min")?c.data("default-min"):100,h=c.data("default-max")?c.data("default-max"):500,i=c.data("currency")?c.data("currency"):"$",j=b.find(".range-from"),k=b.find(".range-to");j.val(i+" "+g),k.val(i+" "+h),c.slider({range:!0,min:d,max:e,step:f,values:[g,h],slide:function(a,b){j.val(i+" "+b.values[0]),k.val(i+" "+b.values[1])}})}}),a("#testimonials").each(function(){var b=a(this),c=b.find(".testimonial-list"),d=c.find(".testimonial"),e=!!b.data("interval")&&parseInt(b.data("interval"))>0,f=d.first().find(".portrait img");f.length>0&&c.before('<div class="active-portrait"><img src="'+f.attr("src")+'" alt="'+f.attr("alt")+'"></div>'),c.owlCarousel({autoPlay:e,slideSpeed:300,pagination:!1,paginationSpeed:400,singleItem:!0,addClassActive:!0,afterMove:function(){var a;b.find(".active-portrait").fadeOut(200,function(){a=c.find(".owl-item.active .portrait img"),a.length>0&&(b.find(".active-portrait img").attr("src",a.attr("src")),b.find(".active-portrait img").attr("alt",a.attr("alt"))),b.find(".active-portrait").fadeIn(200)})}}),b.find(".navigation .prev").click(function(){c.trigger("owl.prev")}),b.find(".navigation .next").click(function(){c.trigger("owl.next")})}),a("#bottom-panel .newsletter-widget form").submit(function(){var b=a(this);return b.uouFormValid()?void b.find(".alert-message.warning:visible").slideUp(300):(b.find(".alert-message.warning").slideDown(300),!1)}),a("#bottom-panel .twitter-feed").each(function(){a(this).uouTwitterFeed()}),a(window).resize(function(){b()!==c&&(c=b(),a(".header-navbar, .header-form, .header-nav, .header-nav ul, .header-menu, .header-search, .header-tools, .sub-menu").removeAttr("style"),a(".submenu-toggle .fa").removeClass("fa-chevron-up").addClass("fa-chevron-down"),a(".header-btn").removeClass("hover"))}),a("body").hasClass("enable-style-switcher")){var d='<div id="style-switcher"><button class="style-switcher-toggle"><i class="ico fa fa-cog"></i></button>';d+='<div class="style-switcher-content"><ul class="custom-list skin-list">',d+='<li><button class="skin-default active" data-skin="default"><span>Default</span></button></li>',d+='<li><button class="skin-blue" data-skin="blue"><span>Blue</span></button></li>',d+='<li><button class="skin-yellow" data-skin="yellow"><span>Yellow</span></button></li>',d+="</ul></div></div>",a("body").append(d),a("#style-switcher").each(function(){var b=a(this),c=b.find(".style-switcher-toggle"),d=b.find(".skin-list button"),e={},f=function(){a("html").hasClass("localstorage")&&(localStorage.style_switcher_settings=JSON.stringify(e))};a("html").hasClass("localstorage")&&localStorage.style_switcher_settings&&(e=JSON.parse(localStorage.style_switcher_settings),"undefined"!=typeof e.skin&&(d.filter(".active").removeClass("active"),d.filter('[data-skin="'+e.skin+'"]').addClass("active"),a("head #skin-temp").length<1&&a("head").append('<link id="skin-temp" rel="stylesheet" type="text/css" href="library/css/skins/'+e.skin+'.css">'))),c.click(function(){b.toggleClass("active")}),d.click(function(){d.filter(".active").removeClass("active"),a(this).toggleClass("active"),e.skin=a(this).data("skin"),f(),a("head #skin-temp").length<1?a("head").append('<link id="skin-temp" rel="stylesheet" type="text/css" href="library/css/skins/'+a(this).data("skin")+'.css">'):a("#skin-temp").attr("href","library/css/skins/"+a(this).data("skin")+".css")})})}a(".thumb-view").addClass("active"),a(".list-grid-view button").on("click",function(b){a(this).hasClass("thumb-view")?(a(this).addClass("active"),a(".without-thumb").removeClass("active"),a(".grid-view").removeClass("active"),a(".all-menu-details").removeClass("thumb"),a(".menu-with-details").removeClass("menu-with-details").addClass("item-list"),a(".for-list").show()):a(this).hasClass("without-thumb")?(a(this).addClass("active"),a(".thumb-view").removeClass("active"),a(".grid-view").removeClass("active"),a(".all-menu-details").addClass("thumb"),a(".menu-with-details").removeClass("menu-with-details").addClass("item-list"),a(".for-list").show()):a(this).hasClass("grid-view")&&(a(".thumb-view").removeClass("active"),a(".without-thumb").removeClass("active"),a(this).addClass("active"),a(".item-list").addClass("menu-with-details").removeClass("item-list"),a(".m-with-details").show(),a(".for-list").hide())});var e=a("#main-wrapper .all-menu-details .dropdown-option");e.hide(),a(".toggle").click(function(){a(this).toggleClass("active"),a(this).parent().parent().next().slideToggle(300),a(this).parent().parent().toggleClass("red")});var f=a(".category .toggle-content ul");f.hide(),a("#main-wrapper .side-panel .sd-panel-heading").hide(),a("#main-wrapper .side-panel .toggle-main-title").click(function(){a(this).toggleClass("active").next().slideToggle()}),a("#main-wrapper .side-panel .sd-panel-heading .slideToggle").hide(),a("#main-wrapper .side-panel .toggle-title").click(function(){a(this).toggleClass("active").next().slideToggle()});var g=a("#header .header-top-bar .call-us"),h=g.find("input"),i=a("#header .header-top-bar .call-us .open-now"),j=a("#header .header-top-bar .call-us .close-now");j.hide(),h.change(function(){h.is(":checked")?(i.show(),j.hide()):(i.hide(),j.show())}),a(".qty-cart button").click(function(b){a(this).toggleClass("active"),b.preventDefault()});var k=a("#thumb-slide-section");k.owlCarousel({itemsCustom:[[0,2],[450,3],[600,4],[700,6],[1e3,8],[1200,14],[1400,14],[1600,15]],navigation:!0}),a("#slide-content").owlCarousel({autoPlay:4e3,stopOnHover:!0,itemsCustom:[[0,1],[450,1],[600,1],[700,1],[1e3,2],[1200,2],[1400,2],[1600,2]]}),a("#map_canvas").gmap({scrollwheel:!1}).bind("init",function(b,c){a("#map_canvas").gmap("addMarker",{position:"57.7973333,12.0502107",bounds:!0}).click(function(){a("#map_canvas").gmap("openInfoWindow",{content:"TakeAway"},this)}),a("#map_canvas").gmap("option","zoom",14)})})}(jQuery);