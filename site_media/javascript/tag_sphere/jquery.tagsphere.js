/*
Plugin: 3D Tag Sphere
Version: 0.1
Author: Ian George
Website: http://www.iangeorge.net
Tools: Emacs, js2-mode, jquery
Tested on: IE6, IE7, IE8, Firefox 3.6 Linux, Firefox 3.5 Windows, Chrome Linux / Windows
Requirements: Optional jquery.mousewheel for zooming

Description: 3d tag cloud, rotates with mouse / touch drag and zooms in and out.

Options:
  Option            default            Comments
  --------------------------------------------------

  zoom              90                 Initial zoom level
  max_zoom          120      
  min_zoom          25        
  zoom_factor       2                  Speed of zoom by the mouse wheel
  rotate_factor     0.45               In degrees, the amount that the sphere rotates. Negative values reverse the direction.
  fps               10                 Defines the (target) number of times the animation will be updated per second
  centrex           250                Horizontal rotation centre in the container <div>
  centrey           250                Vertical rotation centre in the container <div>
  min_font_size     12
  max_font_size     32
  font_units        'px'
  random_points     50                 Adds some random points on to the sphere to enhance the effect
  init_motion_x     0                  x (horizontal) value for the initial rotation
  init_motion_y     0                  y (vertical) value for the initial rotation

Usage:
 Vanilla:
    $('.tags').tagcloud();

 Centered in a 200 x 200 container:
    $('.tags').tagcloud({centrex:100,centrey:100});

 With a different update speed
    $('.selector').tagcloud({fps:24});

Markup:
 Must be an unordered list in a div with links in the list items. 
 rel="[number]" is optional but necessary for ranking by font-size.
 <div class="tags">
 <ul>
   <li><a href="#" rel="20">link 1</a></li>
   <li><a href="#" rel="20">link 2</a></li>
   <li><a href="#" rel="20">link 3</a></li>
   <li><a href="#" rel="20">link 4</a></li>
   <li><a href="#" rel="20">link 5</a></li>
 </ul>
 */

var HEX = new Array("0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f");


/* fixed-size movement queue, used for averaging touch / drag 
 * movement over a number of events */
function mqueue(size, negate){
    this.items = new Array();
    this.size = size;
    this.last = 0;

    this.reset = function(){
      this.items = new Array();  
    };

    this.add = function(abs_val, start){
        var val = 0;

        if (this.last == 0 || start) this.last = abs_val;

        // calculate val as movement rather than absolute coordinates
        if(this.items.length > 0){
            if(negate){ 
                val = this.last - abs_val;
            }else{
                val = abs_val - this.last;
            }
        }else{
            val = abs_val;
        }
        this.last = abs_val;
        // add item to list and remove last item if list is too large
        this.items.push(val);

        if(this.items.length > this.size){
            this.items.shift();
        }
    };
    
    this.avg = function(){
        var total = 0;
        for(i in this.items){
            total += this.items[i];
        }
        var rv = (total / size);
        return rv;
    };
}

(function($){

     // jquery plugin hook
     $.fn.tagcloud = function(options){
        
         // overwrite defaults with user-specified
         var opts = $.extend($.fn.tagcloud.defaults, options);
         opts.drawing_interval = 1/(opts.fps/1000);
         
         //create a new class for every matching element
         $(this).each(function(){
                          new TagCloudClass($(this), opts);
                      });
         return this;         
     };

     //default values for setup
     $.fn.tagcloud.defaults = {
         zoom: 90,
         max_zoom: 120,
         min_zoom: 25,
         zoom_factor: 5, //multiplication factor for wheel delta
         rotate_factor: 2, // multiplication factor for rotation
         fps: 20, // frames per second
         centrex: 250, // set centre of display
         centrey: 250,
         min_font_size: 12, //font limits and units
         max_font_size: 32,
         font_units: 'px',
         random_points: 0,         
         init_motion_x: 0,
         init_motion_y: 0,
         decay: 0.90
     };

     var TagCloudClass = function(el, options){
         $(el).css('position', 'relative');

         // general values
         var eyez = -500;

         // set rotation (in this case, 5degrees)
         var rad = Math.PI/180;
         var global_cos = Math.cos(0);

         // per-instance values
         var dirty = true;
         var container = $(el);
         var id_stub = 'tc_' + $(el).attr('id') + "_";
         var opts = options;
         var zoom = opts.zoom;
         var depth;
	 var points_meta = [];
         var points_data = [];

         var vectorx = opts.init_motion_x;
         var vectory = opts.init_motion_y;
         var motionx = new mqueue(50, true);
         var motiony = new mqueue(50, false);
         var dragging = false;
         var mousex = 0;
         var mousey = 0;

         var drawing_interval;
         var cmx = options.centrex; 
         var cmy = options.centrey;
         var bg_colour;
         if (options.background_colour){
             bg_colour = parsecolour(options.background_colour);
         }else{
             bg_colour = parsecolour($(el).css('background-color'));
         }
         
         function parsecolour(colour){
             function parse_rgb_colour(colour){
                 rgb = colour.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
                 if(!rgb) return {"r":255, "g":255, "b":255};

                 if(rgb.length > 3){
                     return {"r" : parseInt(rgb[1]), "g": parseInt(rgb[2]), "b" : parseInt(rgb[3])};                 
                 }else{  
                     return {"r":0, "g":0, "b":0};
                 }
             }
             function parse_hex_colour(colour){
                 var r = 0, g = 0, b = 0;
                 if(colour.length > 4)
                 {
                     r = parseInt(colour.substr(1,2), 16);
                     g = parseInt(colour.substr(3,2), 16);
                     b = parseInt(colour.substr(5,2), 16);
                 }
                 else
                 {
                     r = parseInt(colour.substr(1,1)+colour.substr(1,1), 16);
                     g = parseInt(colour.substr(2,1)+colour.substr(2,1), 16);
                     b = parseInt(colour.substr(3,1)+colour.substr(3,1), 16);
                 }
                 return {"r" : r, "g" : g, "b" : b};
             }

             if(colour.substr(0, 1) === '#')
             {
                 return parse_hex_colour(colour);
             }
             else if (colour.substr(0,3) === 'rgb')
             {
                 return parse_rgb_colour(colour);
             }
             else{
                 //somehow we've got a plain old string as a colour
                 if(window.console != undefined)
                     console.log("unable to parse:'" + colour + "' please ensure background and foreground colors for the container are set as hex values");
                 return null;
             }
         }
             
         function getcolour(num, fg_colour){
             if(num>256){num=256;}
             if(num<0){num=0;}

             var r = getshade(bg_colour.r, fg_colour.r, num);
             var g = getshade(bg_colour.g, fg_colour.g, num);
             var b = getshade(bg_colour.b, fg_colour.b, num);

             var ret  = "rgb(" + r + ", "+ g + ", " + b + ")"; 
             return ret;
         }

         function getshade(lbound, ubound, dist){
             var scope = ubound - lbound;
             var dist_percent = scope / 100;
             var shade = Math.round(lbound + (dist * dist_percent));
             return shade;
         }

         function zoomed(by){
             zoom += by * opts.zoom_factor;

             if (zoom > opts.max_zoom) {
	         zoom = opts.max_zoom;
             }
             if (zoom < opts.min_zoom) {
	         zoom = opts.min_zoom;
             }

             depth = -(zoom * (eyez - opts.max_zoom) / 100) + eyez;
             dirty = true;
         }

         function decay_me(vector){ 
             if(Math.abs(vector) < 0.5){
                 vector = 0;
             }else{
                 if(vector > 0){
                     vector *= opts.decay;
                 }
                 if (vector < 0){
                     vector *= opts.decay;
                 }
             }
             return vector;
         }

         function move(){
             if(vectorx != 0 || vectory != 0){
                 
                 var factor = options.rotate_factor;
                 var tx = vectorx * rad * factor;
                 var ty = vectory * rad * factor;

                 for(var p in points_data)
                 {                 
                     var sin_x = Math.sin(tx);
                     var cos_x = Math.cos(tx);
                     var sin_y = Math.sin(ty);
                     var cos_y = Math.cos(ty);

                     var x = points_data[p].x;
                     var z = points_data[p].z;
	             points_data[p].x = x * cos_x + z * sin_x;
	             points_data[p].z = z * cos_x - x * sin_x;

                     var y = points_data[p].y;
                     var z = points_data[p].z;
                     points_data[p].y = y * cos_y - z * sin_y;
                     points_data[p].z = y * sin_y + z * cos_y;

                 }                
                 
                 dirty = true;
             }
         }

         function decay_all(){
             vectorx = decay_me(vectorx);
             vectory = decay_me(vectory);
             if(!dragging){
                 motionx.add(0);
                 motiony.add(0);
             }
         }

         function draw(){
             // calculate 2D coordinates
             if(dirty){
                 var smallz = 10000; 
                 var bigz = -10000;
                 
                 for(var r_p in points_data){
	             if(points_data[r_p].z < smallz){smallz = points_data[r_p].z;}
	             if(points_data[r_p].z > bigz){bigz = points_data[r_p].z;}
                 }
                 var minz = Math.min(smallz, bigz);
                 var maxz = Math.max(smallz, bigz);
                 var diffz = maxz - minz;
                 
                 for(var s_p in points_data){ 
                     //normalise depth
	             var u = (depth - eyez)/(points_data[s_p].z - eyez);

                     // calculate normalised grey value
                     var dist = Math.round(((maxz - points_data[s_p].z)/diffz) * 100);
                     var dist_colour = getcolour(dist, points_data[s_p].colour);
                     //set new 2d positions for the data
                     points_data[s_p].element.css('color',dist_colour);
                     points_data[s_p].element.css('z-index', dist);
                     points_data[s_p].element.css('left', u * points_data[s_p].x + cmx - points_data[s_p].cwidth);
                     points_data[s_p].element.css('top', u * points_data[s_p].y + cmy); 
                 }			
                 dirty = false;
             }
             move(vectorx, vectory);
             decay_all();
         }

         function debug(msg){
             $("#debug").append('<p>'+msg+'</p>');
         }

         // number of elements we're adding and placeholders for range values
         points_meta.count = $('li a', container).length;
         points_meta.largest = 1;
         points_meta.smallest = 0;


         // Run through each li > a in the container and create an absolutely-positioned div in its place
         // Also need to create a data structure to keep state between calls to draw()
         // Data structure is as follows:
         // 
         // points{
         //     'count':0,                      //Total number of points
         //     'largest':0,                    //largest 'size' value
         //     'smallest':0,                   //Smallest 'size' value
         //     'data':{
         //         'id':"",                    //HTML id for element
         //         'size':0,                   //Size (from rel attribute on <a>)
         //         'theta':0.0,                //Angle on sphere (used to calculate initial cartesian position)
         //         'phi': 0.0,                 //Angle on sphere (used to calculate initial cartesian position)
         //         'x':0.0,                    //Cartesian position in 3d space
         //         'y':0.0,                    //Cartesian position in 3d space
         //         'z':0.0,                    //Cartesian position in 3d space
         //         'element':obj               //jquery dom element
         //     }
         // }
         $('li a', container).each(function(idx, val){

                                       var sz = parseInt($(this).attr('rel'));
                                       if(sz == 0) 
                                           sz = 1;
                                       var point_id = id_stub + idx;
                                       points_data[idx] = {
                                           size:sz
                                       };

                                       // plot the points on a sphere
                                       // from: http://www.math.niu.edu/~rusin/known-math/97/spherefaq
                                       // for k=1 to N do
                                       //     h = -1 + 2*(k-1)/(N-1)
                                       //     theta[k] = arccos(h)
                                       //     if k=1 or k=N then phi[k] = 0
                                       //     else phi[k] = (phi[k-1] + 3.6/sqrt(N*(1-h^2))) mod (2*pi)
                                       // endfor

                                       // In Cartesian coordinates the required point on a sphere of radius 1 is
                                       // (cos(theta)*sin(phi), sin(theta)*sin(phi), cos(phi))
                                       
                                       var h = -1 + 2*(idx)/(points_meta.count-1);
                                       points_data[idx].theta = Math.acos(h);
                                       if(idx == 0 || idx == points_meta.count-1){
                                           points_data[idx].phi = 0;
                                       }
                                       else{
                                           points_data[idx].phi = (points_data[idx-1].phi + 3.6/Math.sqrt(points_meta.count*(1-Math.pow(h,2)))) % (2 * Math.PI);
                                       }

                                       points_data[idx].x = Math.cos(points_data[idx].phi) * Math.sin(points_data[idx].theta) * (cmx/2);
                                       points_data[idx].y = Math.sin(points_data[idx].phi) * Math.sin(points_data[idx].theta) * (cmy/2);
                                       points_data[idx].z = Math.cos(points_data[idx].theta) * (cmx/2);
                                       points_data[idx].colour = parsecolour($(this).css('color'));

                                       if(sz > points_meta.largest) points_meta.largest = sz;
                                       if(sz < points_meta.smallest) points_meta.smallest = sz;

                                       $(this).css('position','absolute');
                                       $(this).addClass('point');
                                       $(this).attr('id', point_id);

                                       //container.append('<div id="'+ point_id +'" class="point" style="position:absolute;display:none;"><a href=' + $(this).attr('href')  + '>' + $(this).html()  + '</a></div>');
                                       points_data[idx].element = $('#'+point_id);

                                   });

         //tag size and font size ranges 
         var sz_range = points_meta.largest - points_meta.smallest + 1; 
         var sz_n_range = opts.max_font_size - opts.min_font_size + 1;
         
         //set font size to normalised tag size
         for(var p in points_data){
             var sz = points_data[p].size;
             var sz_n = parseInt((sz / sz_range) * sz_n_range) + opts.min_font_size;
             if(!points_data[p].element.hasClass('background')){
                 points_data[p].element.css('font-size', sz_n); 
             }
             //store element width / 2 so we can centre the text around the point later.
             points_data[p].cwidth = points_data[p].element.width()/2;
         }
         // bin original html
         //$('ul', container).remove();

         //set up initial view
         depth = -(zoom * (eyez - opts.max_zoom) / 100) + eyez;
         draw();


         //call draw every so often
         drawing_interval = setInterval(draw, opts.drawing_interval);

         container.bind('touchstart', function(evt){
                            evt.preventDefault();
                            var touch = evt.originalEvent.touches[0] || evt.originalEvent.changedTouches[0];

                            dragging = true;

                            motionx.add(touch.pageX, true);
                            motiony.add(touch.pageY, true);

                        });

         container.bind('touchmove', function(evt){
                            evt.preventDefault();
                            var touch = evt.originalEvent.touches[0] || evt.originalEvent.changedTouches[0];

                            motionx.add(touch.pageX, false);
                            motiony.add(touch.pageY, false);
                            vectorx = motionx.avg();
                            vectory = motiony.avg();
                        });

         container.bind('touchend', function(evt){
                            evt.preventDefault();

                            dragging = false;
                            motionx.reset();
                            motiony.reset();

                        });



         container.mousemove(function(evt){    
                                 if (dragging){
                                     motionx.add(evt.pageX, false);
                                     motiony.add(evt.pageY);
                                     vectorx = motionx.avg();
                                     vectory = motiony.avg();
                                 }
                                 evt.preventDefault();
                             });

         container.mousedown(function(evt){
                                 if(evt.which == 1){
                                     dragging = true;
                                     motionx.add(evt.pageX, true);
                                     motiony.add(evt.pageY, true);
                                 }
                                 evt.preventDefault();
                                 return false;
                             });

         container.mouseup(function(evt){
                               if(evt.which == 1){
                                   dragging = false;
                                   motionx.reset();
                                   motiony.reset();
                               }
                             });
         
         container.mouseleave(function(evt){
             dragging = false;
             motionx.reset();
             motiony.reset();
         });

         container.mousewheel(function(evt, delta){
                                  zoomed(delta);
                                  evt.preventDefault();
                                  return false;
                              });

         $('.point a').click(function(e){
                                 if(dragging){
                                     e.preventDefault();
                                     return false;                                     
                                 }
                                 return true;
                             });
     };
          
 })(jQuery);
