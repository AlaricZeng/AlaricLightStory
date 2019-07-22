new Vue({
	el: '#login-container',
	data: {
		username: '',
		password: ''
	},
	methods: {
		submit: function() {
			$('#login-form').submit();
		}
	}
})