angular.module "throwdown"
  .directive 'acmeMalarkey', ->

    MalarkeyController = ($log) ->
      vm = this
      vm.contributors = ['Ali', 'Thomas', 'Roujia']
      return

    linkFunc = (scope, el, attr, vm) ->
      typist = malarkey(el[0],
        typeSpeed: 40
        deleteSpeed: 40
        pauseDelay: 800
        loop: true
        postfix: ' ')
      el.addClass 'acme-malarkey'
      angular.forEach vm.contributors, (contributor) ->
        typist.type(contributor).pause().delete()
        return
      return

    directive =
      restrict: 'E'
      scope: extraValues: '='
      template: '&nbsp;'
      link: linkFunc
      controller: MalarkeyController
      controllerAs: 'vm'
