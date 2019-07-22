new Vue({
	el: '#image-management-container',
	data: {
		select: null,
		storyTitles: ['None'],
		stories: {},
		imageTableHeaders: [
			{
				text: 'Pictures',
				align: 'left',
				sortable: false,
				value: 'url'
			},
			{
				text: 'Linked Story',
				align: 'left',
				value: 'story'
			},
			{
				text: 'Display?',
				align: 'left',
				value: 'display'
			},
			{ 
				text: 'Actions', 
				value: 'url', 
				sortable: false 
			}
		],
		imageInfo: [],
		editDialog:false,
		editedIndex: -1,
	    editedItem: {
	    	id: '',
	     	url: '',
	     	story: '',
	     	display: false
	    },
	    defaultItem: {
	    	id: '',
	    	url: '',
	      	story: '',
	      	display: false
	    },
	},
	mounted: function() {
		var that = this;

		$.get( "http://127.0.0.1:5000/admin/get_story_list")
			.done(function(data) {
				data.forEach(function(value, index) {
					that.stories[value[0]] = value[1]
					that.storyTitles.push(that.generateStoryTitle(value[0], value[1]));
				});
			});

		$.get( "http://127.0.0.1:5000/admin/get_image_list")
			.done(function(data) {
				data.forEach(function(value, index) {
					that.imageInfo.push({
						id: value[0],
						url: '/static/images/thumbnails/' + value[1],
						story: that.stories[value[2]] ? that.generateStoryTitle(value[2], that.stories[value[2]]) : 'none',
						display: value[3]
					});
				});
			});
	},
	methods: {
		submit: function() {
			$('#upload-image-form').submit();
		},

		editItem: function(item) {
      		this.editedIndex = this.imageInfo.indexOf(item);
      		this.editedItem = Object.assign({}, item);
      		this.editDialog = true;
      	},

      	deleteItem: function(item) {
      		const index = this.imageInfo.indexOf(item);
      		var confirmed = confirm('Are you sure you want to delete this item?');
      		var that = this;
      		if (confirmed) {
      			$.post( "http://127.0.0.1:5000/admin/delete_image", {id: item.id})
      			.done(function(data) {
					that.imageInfo.splice(index, 1)
				});
      		}
    	},

      	save: function() {
	 		if (this.editedIndex > -1) {
	 			var that = this;
	       		$.post( "http://127.0.0.1:5000/admin/edit_image_info", 
	       			{id: that.editedItem.id, storyTitle: that.editedItem.story, display: that.editedItem.display})
	       		.done(function(data) {
					Object.assign(that.imageInfo[that.editedIndex], that.editedItem);
				});
	      	} else {
	        	this.imageInfo.push(this.editedItem);
	      	}
	      	this.close();
	    },

	    close: function() {
      		this.editDialog = false;
      		setTimeout(() => {
        		this.editedItem = Object.assign({}, this.defaultItem);
        		this.editedIndex = -1;
      		}, 300);
    	},

    	generateStoryTitle: function(storyIndex, storyTitle) {
    		return storyIndex + ' - ' + storyTitle
    	}
	}
});


new Vue({
	el: '#story-management-container',
	data: {
		storyTableHeaders: [
			{
				text: 'Id',
				align: 'left',
				value: 'id'
			},
			{
				text: 'Title',
				align: 'left',
				value: 'title'
			},
			{ 
				text: 'Actions', 
				value: 'id', 
				sortable: false 
			}
		],
		storyInfo: [],
		editDialog:false,
		editedIndex: -1,
	    editedItem: {
	    	id: '',
	     	title: ''
	    },
	    defaultItem: {
	    	id: '',
	    	title: ''
	    },
	    rules: {
        	required: value => !!value || 'Required.'
        },
        uploadedStoryFile: '',
	    uploadedStoryTitle: '',
	    editedStoryFile: ''
	},
	mounted: function() {
		var that = this;

		$.get( "http://127.0.0.1:5000/admin/get_story_list")
			.done(function(data) {
				data.forEach(function(value, index) {
					that.storyInfo.push({
						id: value[0],
						title: value[1]
					})
				});
			});
	},
	computed: {
		uploadNewStoryFormIsValid: function() {
			return this.uploadedStoryTitle &&
					this.uploadedStoryFile;
		},
		uploadExistStoryFormIsValid: function() {
			return this.editedItem.title &&
					this.editedStoryFile;
		},
	},
	methods: {
		updateNewStoryFile: function(event) {
			this.uploadedStoryFile = event.target.files;
		},

		updateExistStoryFile: function(event) {
			this.editedStoryFile = event.target.files;
		},

		submit: function() {
			$('#upload-story-form').submit();
		},

		editItem: function(item) {
      		this.editedIndex = this.storyInfo.indexOf(item);
      		this.editedItem = Object.assign({}, item);
      		this.editDialog = true;
      	},

      	deleteItem: function(item) {
      		const index = this.storyInfo.indexOf(item);
      		var confirmed = confirm('Are you sure you want to delete this story?');
      		var that = this;
      		if (confirmed) {
      			$.post( "http://127.0.0.1:5000/admin/delete_story", {id: item.id})
      			.done(function(data) {
					that.storyInfo.splice(index, 1)
				});
      		}
    	},

      	save: function() {
	 		if (this.editedIndex > -1) {
	 			$('#edit-story-form').submit();
				Object.assign(that.storyInfo[that.editedIndex], that.editedItem);
	      	} else {
	        	this.storyInfo.push(this.editedItem);
	      	}
	      	this.close();
	    },

	    downloadItem: function(item) {
      		$.post( "http://127.0.0.1:5000/admin/download_story", {title: item.title})
      		.done(function(data) {
				window.location.href = data;
			});
    	},

	    close: function() {
      		this.editDialog = false;
      		setTimeout(() => {
      			$('#update-exist-file').val('');
      			this.editedStoryFile = '';
        		this.editedItem = Object.assign({}, this.defaultItem);
        		this.editedIndex = -1;
      		}, 300);
    	}
	}
});