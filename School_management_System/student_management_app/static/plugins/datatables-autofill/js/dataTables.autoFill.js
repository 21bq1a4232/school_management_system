/*! AutoFill 2.3.4
 * ©2008-2019 SpryMedia Ltd - datatables.net/license
 */

/**
 * @summary     AutoFill
 * @description Add Excel like click and drag auto-fill options to DataTables
 * @version     2.3.4
 * @file        dataTables.autoFill.js
 * @author      SpryMedia Ltd (www.sprymedia.co.uk)
 * @contact     www.sprymedia.co.uk/contact
 * @copyright   Copyright 2010-2019 SpryMedia Ltd.
 *
 * This source file is free software, available under the following license:
 *   MIT license - http://datatables.net/license/mit
 *
 * This source file is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
 * or FITNESS FOR A PARTICULAR PURPOSE. See the license files for details.
 *
 * For details please refer to: http://www.datatables.net
 */
(function( factory ){
	if ( typeof define === 'function' && define.amd ) {

		define( ['jquery', 'datatables.net'], function ( $ ) {
			return factory( $, window, document );
		} );
	}
	else if ( typeof exports === 'object' ) {

		module.exports = function (root, $) {
			if ( ! root ) {
				root = window;
			}

			if ( ! $ || ! $.fn.dataTable ) {
				$ = require('datatables.net')(root, $).$;
			}

			return factory( $, root, root.document );
		};
	}
	else {

		factory( jQuery, window, document );
	}
}(function( $, window, document, undefined ) {
'use strict';
var DataTable = $.fn.dataTable;


var _instance = 0;

/** 
 * AutoFill provides Excel like auto-fill features for a DataTable
 *
 * @class AutoFill
 * @constructor
 * @param {object} oTD DataTables settings object
 * @param {object} oConfig Configuration object for AutoFill
 */
var AutoFill = function( dt, opts )
{
	if ( ! DataTable.versionCheck || ! DataTable.versionCheck( '1.10.8' ) ) {
		throw( "Warning: AutoFill requires DataTables 1.10.8 or greater");
	}


	this.c = $.extend( true, {},
		DataTable.defaults.autoFill,
		AutoFill.defaults,
		opts
	);

	/**
	 * @namespace Settings object which contains customisable information for AutoFill instance
	 */
	this.s = {

		dt: new DataTable.Api( dt ),


		namespace: '.autoFill'+(_instance++),


		scroll: {},


		scrollInterval: null,

		handle: {
			height: 0,
			width: 0
		},

		/**
		 * Enabled setting
		 * @type {Boolean}
		 */
		enabled: false
	};


	/**
	 * @namespace Common and useful DOM elements for the class instance
	 */
	this.dom = {

		handle: $('<div class="dt-autofill-handle"/>'),

		/**
		 * @type {Object} Selected cells outline - Need to use 4 elements,
		 *   otherwise the mouse over if you back into the selected rectangle
		 *   will be over that element, rather than the cells!
		 */
		select: {
			top:    $('<div class="dt-autofill-select top"/>'),
			right:  $('<div class="dt-autofill-select right"/>'),
			bottom: $('<div class="dt-autofill-select bottom"/>'),
			left:   $('<div class="dt-autofill-select left"/>')
		},


		background: $('<div class="dt-autofill-background"/>'),


		list: $('<div class="dt-autofill-list">'+this.s.dt.i18n('autoFill.info', '')+'<ul/></div>'),


		dtScroll: null,


		offsetParent: null
	};



	this._constructor();
};



$.extend( AutoFill.prototype, {
	/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
	 * Public methods (exposed via the DataTables API below)
	 */
	enabled: function ()
	{
		return this.s.enabled;
	},


	enable: function ( flag )
	{
		var that = this;

		if ( flag === false ) {
			return this.disable();
		}

		this.s.enabled = true;

		this._focusListener();

		this.dom.handle.on( 'mousedown', function (e) {
			that._mousedown( e );
			return false;
		} );

		return this;
	},

	disable: function ()
	{
		this.s.enabled = false;

		this._focusListenerRemove();

		return this;
	},


	/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
	 * Constructor
	 */

	/**
	 * Initialise the RowReorder instance
	 *
	 * @private
	 */
	_constructor: function ()
	{
		var that = this;
		var dt = this.s.dt;
		var dtScroll = $('div.dataTables_scrollBody', this.s.dt.table().container());


		dt.settings()[0].autoFill = this;

		if ( dtScroll.length ) {
			this.dom.dtScroll = dtScroll;


			if ( dtScroll.css('position') === 'static' ) {
				dtScroll.css( 'position', 'relative' );
			}
		}

		if ( this.c.enable !== false ) {
			this.enable();
		}

		dt.on( 'destroy.autoFill', function () {
			that._focusListenerRemove();
		} );
	},


	/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
	 * Private methods
	 */

	/**
	 * Display the AutoFill drag handle by appending it to a table cell. This
	 * is the opposite of the _detach method.
	 *
	 * @param  {node} node TD/TH cell to insert the handle into
	 * @private
	 */
	_attach: function ( node )
	{
		var dt = this.s.dt;
		var idx = dt.cell( node ).index();
		var handle = this.dom.handle;
		var handleDim = this.s.handle;

		if ( ! idx || dt.columns( this.c.columns ).indexes().indexOf( idx.column ) === -1 ) {
			this._detach();
			return;
		}

		if ( ! this.dom.offsetParent ) {

			this.dom.offsetParent = $( dt.table().node() ).offsetParent();
		}

		if ( ! handleDim.height || ! handleDim.width ) {


			handle.appendTo( 'body' );
			handleDim.height = handle.outerHeight();
			handleDim.width = handle.outerWidth();
		}


		var offset = this._getPosition( node, this.dom.offsetParent );

		this.dom.attachedTo = node;
		handle
			.css( {
				top: offset.top + node.offsetHeight - handleDim.height,
				left: offset.left + node.offsetWidth - handleDim.width
			} )
			.appendTo( this.dom.offsetParent );
	},


	/**
	 * Determine can the fill type should be. This can be automatic, or ask the
	 * end user.
	 *
	 * @param {array} cells Information about the selected cells from the key
	 *     up function
	 * @private
	 */
	_actionSelector: function ( cells )
	{
		var that = this;
		var dt = this.s.dt;
		var actions = AutoFill.actions;
		var available = [];


		$.each( actions, function ( key, action ) {
			if ( action.available( dt, cells ) ) {
				available.push( key );
			}
		} );

		if ( available.length === 1 && this.c.alwaysAsk === false ) {

			var result = actions[ available[0] ].execute( dt, cells );
			this._update( result, cells );
		}
		else {

			var list = this.dom.list.children('ul').empty();


			available.push( 'cancel' );

			$.each( available, function ( i, name ) {
				list.append( $('<li/>')
					.append(
						'<div class="dt-autofill-question">'+
							actions[ name ].option( dt, cells )+
						'<div>'
					)
					.append( $('<div class="dt-autofill-button">' )
						.append( $('<button class="'+AutoFill.classes.btn+'">'+dt.i18n('autoFill.button', '&gt;')+'</button>')
							.on( 'click', function () {
								var result = actions[ name ].execute(
									dt, cells, $(this).closest('li')
								);
								that._update( result, cells );

								that.dom.background.remove();
								that.dom.list.remove();
							} )
						)
					)
				);
			} );

			this.dom.background.appendTo( 'body' );
			this.dom.list.appendTo( 'body' );

			this.dom.list.css( 'margin-top', this.dom.list.outerHeight()/2 * -1 );
		}
	},


	/**
	 * Remove the AutoFill handle from the document
	 *
	 * @private
	 */
	_detach: function ()
	{
		this.dom.attachedTo = null;
		this.dom.handle.detach();
	},


	/**
	 * Draw the selection outline by calculating the range between the start
	 * and end cells, then placing the highlighting elements to draw a rectangle
	 *
	 * @param  {node}   target End cell
	 * @param  {object} e      Originating event
	 * @private
	 */
	_drawSelection: function ( target, e )
	{

		var dt = this.s.dt;
		var start = this.s.start;
		var startCell = $(this.dom.start);
		var end = {
			row: this.c.vertical ?
				dt.rows( { page: 'current' } ).nodes().indexOf( target.parentNode ) :
				start.row,
			column: this.c.horizontal ?
				$(target).index() :
				start.column
		};
		var colIndx = dt.column.index( 'toData', end.column );
		var endRow =  dt.row( ':eq('+end.row+')', { page: 'current' } ); // Workaround for M581
		var endCell = $( dt.cell( endRow.index(), colIndx ).node() );


		if ( ! dt.cell( endCell ).any() ) {
			return;
		}


		if ( dt.columns( this.c.columns ).indexes().indexOf( colIndx ) === -1 ) {
			return;
		}

		this.s.end = end;

		var top, bottom, left, right, height, width;

		top    = start.row    < end.row    ? startCell : endCell;
		bottom = start.row    < end.row    ? endCell   : startCell;
		left   = start.column < end.column ? startCell : endCell;
		right  = start.column < end.column ? endCell   : startCell;

		top    = this._getPosition( top.get(0) ).top;
		left   = this._getPosition( left.get(0) ).left;
		height = this._getPosition( bottom.get(0) ).top + bottom.outerHeight() - top;
		width  = this._getPosition( right.get(0) ).left + right.outerWidth() - left;

		var select = this.dom.select;
		select.top.css( {
			top: top,
			left: left,
			width: width
		} );

		select.left.css( {
			top: top,
			left: left,
			height: height
		} );

		select.bottom.css( {
			top: top + height,
			left: left,
			width: width
		} );

		select.right.css( {
			top: top,
			left: left + width,
			height: height
		} );
	},


	/**
	 * Use the Editor API to perform an update based on the new data for the
	 * cells
	 *
	 * @param {array} cells Information about the selected cells from the key
	 *     up function
	 * @private
	 */
	_editor: function ( cells )
	{
		var dt = this.s.dt;
		var editor = this.c.editor;

		if ( ! editor ) {
			return;
		}


		var idValues = {};
		var nodes = [];
		var fields = editor.fields();

		for ( var i=0, ien=cells.length ; i<ien ; i++ ) {
			for ( var j=0, jen=cells[i].length ; j<jen ; j++ ) {
				var cell = cells[i][j];


				var col = dt.settings()[0].aoColumns[ cell.index.column ];
				var fieldName = col.editField;

				if ( fieldName === undefined ) {
					var dataSrc = col.mData;




					for ( var k=0, ken=fields.length ; k<ken ; k++ ) {
						var field = editor.field( fields[k] );

						if ( field.dataSrc() === dataSrc ) {
							fieldName = field.name();
							break;
						}
					}
				}

				if ( ! fieldName ) {
					throw 'Could not automatically determine field data. '+
						'Please see https://datatables.net/tn/11';
				}

				if ( ! idValues[ fieldName ] ) {
					idValues[ fieldName ] = {};
				}

				var id = dt.row( cell.index.row ).id();
				idValues[ fieldName ][ id ] = cell.set;



				nodes.push( cell.index );
			}
		}



		editor
			.bubble( nodes, false )
			.multiSet( idValues )
			.submit();
	},


	/**
	 * Emit an event on the DataTable for listeners
	 *
	 * @param  {string} name Event name
	 * @param  {array} args Event arguments
	 * @private
	 */
	_emitEvent: function ( name, args )
	{
		this.s.dt.iterator( 'table', function ( ctx, i ) {
			$(ctx.nTable).triggerHandler( name+'.dt', args );
		} );
	},


	/**
	 * Attach suitable listeners (based on the configuration) that will attach
	 * and detach the AutoFill handle in the document.
	 *
	 * @private
	 */
	_focusListener: function ()
	{
		var that = this;
		var dt = this.s.dt;
		var namespace = this.s.namespace;
		var focus = this.c.focus !== null ?
			this.c.focus :
			dt.init().keys || dt.settings()[0].keytable ?
				'focus' :
				'hover';



		if ( focus === 'focus' ) {
			dt
				.on( 'key-focus.autoFill', function ( e, dt, cell ) {
					that._attach( cell.node() );
				} )
				.on( 'key-blur.autoFill', function ( e, dt, cell ) {
					that._detach();
				} );
		}
		else if ( focus === 'click' ) {
			$(dt.table().body()).on( 'click'+namespace, 'td, th', function (e) {
				that._attach( this );
			} );

			$(document.body).on( 'click'+namespace, function (e) {
				if ( ! $(e.target).parents().filter( dt.table().body() ).length ) {
					that._detach();
				}
			} );
		}
		else {
			$(dt.table().body())
				.on( 'mouseenter'+namespace, 'td, th', function (e) {
					that._attach( this );
				} )
				.on( 'mouseleave'+namespace, function (e) {
					if ( $(e.relatedTarget).hasClass('dt-autofill-handle') ) {
						return;
					}

					that._detach();
				} );
		}
	},


	_focusListenerRemove: function ()
	{
		var dt = this.s.dt;

		dt.off( '.autoFill' );
		$(dt.table().body()).off( this.s.namespace );
		$(document.body).off( this.s.namespace );
	},


	/**
	 * Get the position of a node, relative to another, including any scrolling
	 * offsets.
	 * @param  {Node}   node         Node to get the position of
	 * @param  {jQuery} targetParent Node to use as the parent
	 * @return {object}              Offset calculation
	 * @private
	 */
	_getPosition: function ( node, targetParent )
	{
		var
			currNode = node,
			currOffsetParent,
			top = 0,
			left = 0;

		if ( ! targetParent ) {
			targetParent = $( $( this.s.dt.table().node() )[0].offsetParent );
		}

		do {


			var positionTop = currNode.offsetTop;
			var positionLeft = currNode.offsetLeft;


			currOffsetParent = $( currNode.offsetParent );

			top += positionTop + parseInt( currOffsetParent.css('border-top-width') ) * 1;
			left += positionLeft + parseInt( currOffsetParent.css('border-left-width') ) * 1;


			if ( currNode.nodeName.toLowerCase() === 'body' ) {
				break;
			}

			currNode = currOffsetParent.get(0); // for next loop
		}
		while ( currOffsetParent.get(0) !== targetParent.get(0) )

		return {
			top: top,
			left: left
		};
	},


	/**
	 * Start mouse drag - selects the start cell
	 *
	 * @param  {object} e Mouse down event
	 * @private
	 */
	_mousedown: function ( e )
	{
		var that = this;
		var dt = this.s.dt;

		this.dom.start = this.dom.attachedTo;
		this.s.start = {
			row: dt.rows( { page: 'current' } ).nodes().indexOf( $(this.dom.start).parent()[0] ),
			column: $(this.dom.start).index()
		};

		$(document.body)
			.on( 'mousemove.autoFill', function (e) {
				that._mousemove( e );
			} )
			.on( 'mouseup.autoFill', function (e) {
				that._mouseup( e );
			} );

		var select = this.dom.select;
		var offsetParent = $( dt.table().node() ).offsetParent();
		select.top.appendTo( offsetParent );
		select.left.appendTo( offsetParent );
		select.right.appendTo( offsetParent );
		select.bottom.appendTo( offsetParent );

		this._drawSelection( this.dom.start, e );

		this.dom.handle.css( 'display', 'none' );




		var scrollWrapper = this.dom.dtScroll;
		this.s.scroll = {
			windowHeight: $(window).height(),
			windowWidth:  $(window).width(),
			dtTop:        scrollWrapper ? scrollWrapper.offset().top : null,
			dtLeft:       scrollWrapper ? scrollWrapper.offset().left : null,
			dtHeight:     scrollWrapper ? scrollWrapper.outerHeight() : null,
			dtWidth:      scrollWrapper ? scrollWrapper.outerWidth() : null
		};
	},


	/**
	 * Mouse drag - selects the end cell and update the selection display for
	 * the end user
	 *
	 * @param  {object} e Mouse move event
	 * @private
	 */
	_mousemove: function ( e )
	{	
		var that = this;
		var dt = this.s.dt;
		var name = e.target.nodeName.toLowerCase();
		if ( name !== 'td' && name !== 'th' ) {
			return;
		}

		this._drawSelection( e.target, e );
		this._shiftScroll( e );
	},


	/**
	 * End mouse drag - perform the update actions
	 *
	 * @param  {object} e Mouse up event
	 * @private
	 */
	_mouseup: function ( e )
	{
		$(document.body).off( '.autoFill' );

		var that = this;
		var dt = this.s.dt;
		var select = this.dom.select;
		select.top.remove();
		select.left.remove();
		select.right.remove();
		select.bottom.remove();

		this.dom.handle.css( 'display', 'block' );


		var start = this.s.start;
		var end = this.s.end;


		if ( start.row === end.row && start.column === end.column ) {
			return;
		}

		var startDt = dt.cell( ':eq('+start.row+')', start.column+':visible', {page:'current'} );



		if ( $('div.DTE', startDt.node()).length ) {
			var editor = dt.editor();

			editor
				.on( 'submitSuccess.dtaf close.dtaf', function () {
					editor.off( '.dtaf');

					setTimeout( function () {
						that._mouseup( e );
					}, 100 );
				} )
				.on( 'submitComplete.dtaf preSubmitCancelled.dtaf close.dtaf', function () {
					editor.off( '.dtaf');
				} );


			editor.submit();

			return;
		}


		var rows       = this._range( start.row, end.row );
		var columns    = this._range( start.column, end.column );
		var selected   = [];
		var dtSettings = dt.settings()[0];
		var dtColumns  = dtSettings.aoColumns;
		var enabledColumns = dt.columns( this.c.columns ).indexes();




		for ( var rowIdx=0 ; rowIdx<rows.length ; rowIdx++ ) {
			selected.push(
				$.map( columns, function (column) {
					var row = dt.row( ':eq('+rows[rowIdx]+')', {page:'current'} ); // Workaround for M581
					var cell = dt.cell( row.index(), column+':visible' );
					var data = cell.data();
					var cellIndex = cell.index();
					var editField = dtColumns[ cellIndex.column ].editField;

					if ( editField !== undefined ) {
						data = dtSettings.oApi._fnGetObjectDataFn( editField )( dt.row( cellIndex.row ).data() );
					}

					if ( enabledColumns.indexOf(cellIndex.column) === -1 ) {
						return;
					}

					return {
						cell:  cell,
						data:  data,
						label: cell.data(),
						index: cellIndex
					};
				} )
			);
		}

		this._actionSelector( selected );
		

		clearInterval( this.s.scrollInterval );
		this.s.scrollInterval = null;
	},


	/**
	 * Create an array with a range of numbers defined by the start and end
	 * parameters passed in (inclusive!).
	 * 
	 * @param  {integer} start Start
	 * @param  {integer} end   End
	 * @private
	 */
	_range: function ( start, end )
	{
		var out = [];
		var i;

		if ( start <= end ) {
			for ( i=start ; i<=end ; i++ ) {
				out.push( i );
			}
		}
		else {
			for ( i=start ; i>=end ; i-- ) {
				out.push( i );
			}
		}

		return out;
	},


	/**
	 * Move the window and DataTables scrolling during a drag to scroll new
	 * content into view. This is done by proximity to the edge of the scrolling
	 * container of the mouse - for example near the top edge of the window
	 * should scroll up. This is a little complicated as there are two elements
	 * that can be scrolled - the window and the DataTables scrolling view port
	 * (if scrollX and / or scrollY is enabled).
	 *
	 * @param  {object} e Mouse move event object
	 * @private
	 */
	_shiftScroll: function ( e )
	{
		var that = this;
		var dt = this.s.dt;
		var scroll = this.s.scroll;
		var runInterval = false;
		var scrollSpeed = 5;
		var buffer = 65;
		var
			windowY = e.pageY - document.body.scrollTop,
			windowX = e.pageX - document.body.scrollLeft,
			windowVert, windowHoriz,
			dtVert, dtHoriz;



		if ( windowY < buffer ) {
			windowVert = scrollSpeed * -1;
		}
		else if ( windowY > scroll.windowHeight - buffer ) {
			windowVert = scrollSpeed;
		}

		if ( windowX < buffer ) {
			windowHoriz = scrollSpeed * -1;
		}
		else if ( windowX > scroll.windowWidth - buffer ) {
			windowHoriz = scrollSpeed;
		}



		if ( scroll.dtTop !== null && e.pageY < scroll.dtTop + buffer ) {
			dtVert = scrollSpeed * -1;
		}
		else if ( scroll.dtTop !== null && e.pageY > scroll.dtTop + scroll.dtHeight - buffer ) {
			dtVert = scrollSpeed;
		}

		if ( scroll.dtLeft !== null && e.pageX < scroll.dtLeft + buffer ) {
			dtHoriz = scrollSpeed * -1;
		}
		else if ( scroll.dtLeft !== null && e.pageX > scroll.dtLeft + scroll.dtWidth - buffer ) {
			dtHoriz = scrollSpeed;
		}









		if ( windowVert || windowHoriz || dtVert || dtHoriz ) {
			scroll.windowVert = windowVert;
			scroll.windowHoriz = windowHoriz;
			scroll.dtVert = dtVert;
			scroll.dtHoriz = dtHoriz;
			runInterval = true;
		}
		else if ( this.s.scrollInterval ) {

			clearInterval( this.s.scrollInterval );
			this.s.scrollInterval = null;
		}



		if ( ! this.s.scrollInterval && runInterval ) {
			this.s.scrollInterval = setInterval( function () {


				if ( scroll.windowVert ) {
					document.body.scrollTop += scroll.windowVert;
				}
				if ( scroll.windowHoriz ) {
					document.body.scrollLeft += scroll.windowHoriz;
				}


				if ( scroll.dtVert || scroll.dtHoriz ) {
					var scroller = that.dom.dtScroll[0];

					if ( scroll.dtVert ) {
						scroller.scrollTop += scroll.dtVert;
					}
					if ( scroll.dtHoriz ) {
						scroller.scrollLeft += scroll.dtHoriz;
					}
				}
			}, 20 );
		}
	},


	/**
	 * Update the DataTable after the user has selected what they want to do
	 *
	 * @param  {false|undefined} result Return from the `execute` method - can
	 *   be false internally to do nothing. This is not documented for plug-ins
	 *   and is used only by the cancel option.
	 * @param {array} cells Information about the selected cells from the key
	 *     up function, argumented with the set values
	 * @private
	 */
	_update: function ( result, cells )
	{

		if ( result === false ) {
			return;
		}

		var dt = this.s.dt;
		var cell;
		var columns = dt.columns( this.c.columns ).indexes();


		this._emitEvent( 'preAutoFill', [ dt, cells ] );

		this._editor( cells );




		var update = this.c.update !== null ?
			this.c.update :
			this.c.editor ?
				false :
				true;

		if ( update ) {
			for ( var i=0, ien=cells.length ; i<ien ; i++ ) {
				for ( var j=0, jen=cells[i].length ; j<jen ; j++ ) {
					cell = cells[i][j];

					if ( columns.indexOf(cell.index.column) !== -1 ) {
						cell.cell.data( cell.set );
					}
				}
			}

			dt.draw(false);
		}

		this._emitEvent( 'autoFill', [ dt, cells ] );
	}
} );


/**
 * AutoFill actions. The options here determine how AutoFill will fill the data
 * in the table when the user has selected a range of cells. Please see the
 * documentation on the DataTables site for full details on how to create plug-
 * ins.
 *
 * @type {Object}
 */
AutoFill.actions = {
	increment: {
		available: function ( dt, cells ) {
			var d = cells[0][0].label;


			return !isNaN( d - parseFloat( d ) );
		},

		option: function ( dt, cells ) {
			return dt.i18n(
				'autoFill.increment',
				'Increment / decrement each cell by: <input type="number" value="1">'
			);
		},

		execute: function ( dt, cells, node ) {
			var value = cells[0][0].data * 1;
			var increment = $('input', node).val() * 1;

			for ( var i=0, ien=cells.length ; i<ien ; i++ ) {
				for ( var j=0, jen=cells[i].length ; j<jen ; j++ ) {
					cells[i][j].set = value;

					value += increment;
				}
			}
		}
	},

	fill: {
		available: function ( dt, cells ) {
			return true;
		},

		option: function ( dt, cells ) {
			return dt.i18n('autoFill.fill', 'Fill all cells with <i>'+cells[0][0].label+'</i>' );
		},

		execute: function ( dt, cells, node ) {
			var value = cells[0][0].data;

			for ( var i=0, ien=cells.length ; i<ien ; i++ ) {
				for ( var j=0, jen=cells[i].length ; j<jen ; j++ ) {
					cells[i][j].set = value;
				}
			}
		}
	},

	fillHorizontal: {
		available: function ( dt, cells ) {
			return cells.length > 1 && cells[0].length > 1;
		},

		option: function ( dt, cells ) {
			return dt.i18n('autoFill.fillHorizontal', 'Fill cells horizontally' );
		},

		execute: function ( dt, cells, node ) {
			for ( var i=0, ien=cells.length ; i<ien ; i++ ) {
				for ( var j=0, jen=cells[i].length ; j<jen ; j++ ) {
					cells[i][j].set = cells[i][0].data;
				}
			}
		}
	},

	fillVertical: {
		available: function ( dt, cells ) {
			return cells.length > 1 && cells[0].length > 1;
		},

		option: function ( dt, cells ) {
			return dt.i18n('autoFill.fillVertical', 'Fill cells vertically' );
		},

		execute: function ( dt, cells, node ) {
			for ( var i=0, ien=cells.length ; i<ien ; i++ ) {
				for ( var j=0, jen=cells[i].length ; j<jen ; j++ ) {
					cells[i][j].set = cells[0][j].data;
				}
			}
		}
	},




	cancel: {
		available: function () {
			return false;
		},

		option: function ( dt ) {
			return dt.i18n('autoFill.cancel', 'Cancel' );
		},

		execute: function () {
			return false;
		}
	}
};


/**
 * AutoFill version
 * 
 * @static
 * @type      String
 */
AutoFill.version = '2.3.4';


/**
 * AutoFill defaults
 * 
 * @namespace
 */
AutoFill.defaults = {

	alwaysAsk: false,


	focus: null, // focus, click, hover


	columns: '', // all


	enable: true,


	update: null, // false is editor given, true otherwise


	editor: null,


	vertical: true,


	horizontal: true
};


/**
 * Classes used by AutoFill that are configurable
 * 
 * @namespace
 */
AutoFill.classes = {

	btn: 'btn'
};


/*
 * API
 */
var Api = $.fn.dataTable.Api;


Api.register( 'autoFill()', function () {
	return this;
} );

Api.register( 'autoFill().enabled()', function () {
	var ctx = this.context[0];

	return ctx.autoFill ?
		ctx.autoFill.enabled() :
		false;
} );

Api.register( 'autoFill().enable()', function ( flag ) {
	return this.iterator( 'table', function ( ctx ) {
		if ( ctx.autoFill ) {
			ctx.autoFill.enable( flag );
		}
	} );
} );

Api.register( 'autoFill().disable()', function () {
	return this.iterator( 'table', function ( ctx ) {
		if ( ctx.autoFill ) {
			ctx.autoFill.disable();
		}
	} );
} );




$(document).on( 'preInit.dt.autofill', function (e, settings, json) {
	if ( e.namespace !== 'dt' ) {
		return;
	}

	var init = settings.oInit.autoFill;
	var defaults = DataTable.defaults.autoFill;

	if ( init || defaults ) {
		var opts = $.extend( {}, init, defaults );

		if ( init !== false ) {
			new AutoFill( settings, opts  );
		}
	}
} );



DataTable.AutoFill = AutoFill;
DataTable.AutoFill = AutoFill;


return AutoFill;
}));
