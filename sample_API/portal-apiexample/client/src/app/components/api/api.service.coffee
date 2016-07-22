angular.module "throwdown"
  .service "api", ($http) ->
    baseUrl = 'http://10.10.13.102:4040/api'
    endpointList = (endpoint) -> "#{baseUrl}/#{endpoint}"
    endpointId = (endpoint, id) -> "#{baseUrl}/#{endpoint}/#{id}"
    endpointIdVMs = (endpoint, id) -> "#{baseUrl}/#{endpoint}/#{id}/vms"
    @getServices = ->
      return $http.get(endpointList 'services')
      .then(
        (response) -> response.data
        (response) -> []
      )
    @getVNets = ->
      return $http.get(endpointList 'vnets')
      .then(
        (response) -> response.data
        (response) -> []
      )
    return
