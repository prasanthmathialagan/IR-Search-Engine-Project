'use strict';

var app = angular.module('IR', ['ngAnimate', 'ui.bootstrap', 'angularUtils.directives.dirPagination', 'ng-fusioncharts', 'ngRoute'])
    .config(['$routeProvider', '$locationProvider',
        /* Routing */
        function($routeProvider, $locationProvider) {
            $routeProvider

            .when('/', {
                templateUrl: 'partials/search.html',
                controller: 'SearchController',
                active: 'search'
            })
                .when('/search', {
                    templateUrl: 'partials/search.html',
                    controller: 'SearchController',
                    active: 'search'
                })

            .when('/analytics', {
                templateUrl: 'partials/analytics.html',
                controller: 'AnalyticsController',
                active: 'analytics'
            })

            .otherwise({
                redirectTo: '/search'
            });

            $locationProvider.html5Mode(true);
        }
    ]);


app.controller('SearchController', function($scope, $http, $log, $q, $location, $route) {
    $scope.show_top = true;
    $scope.language_map = {
        "en": "English",
        "ru": "Russian",
        "de": "German",
        "fr": "French",
        "ar": "Arabic"
    }

    $log.info($scope.language_map["en"])
    $http.get('http://52.26.115.208:8983/solr/irsearch/select?q=*%3A*&wt=json&indent=true&rows=0&facet=true&facet.field=tweet_hashtags&facet.field=concepts&facet.field=entities&facet.limit=5').then(function(response) {
        $scope.popular_hashtags = response.data.facet_counts.facet_fields.tweet_hashtags
        $scope.popular_concepts = response.data.facet_counts.facet_fields.concepts
        $scope.popular_entities = response.data.facet_counts.facet_fields.entities



        for (var i = 1; i <= $scope.popular_hashtags.length; i += 1)
            $scope.popular_hashtags.splice(i, 1);

        for (var i = 1; i <= $scope.popular_concepts.length; i += 1)
            $scope.popular_concepts.splice(i, 1);

        for (var i = 1; i <= $scope.popular_entities.length; i += 1)
            $scope.popular_entities.splice(i, 1);




    }, function(error) {

    });
    $log.info('Loaded search')

    $scope.update = function(search, id) {
        $scope.search = search;
        $scope.change(id);
    };
    $scope.change = function(id) {

        if (pendingTask) {
            clearTimeout(pendingTask);
        }
        pendingTask = setTimeout(fetch(id), 800);
    };

    var pendingTask;
    $http.defaults.useXDomain = true;


    $scope.filterByLanguage = function(tweet) {

        return $scope.languages[tweet.lang];
    };

    $scope.filterByConcept = function(tweet) {
        var i;
        if (!tweet.concepts)
            return true;

        for (i in tweet.concepts) {
            if ($scope.concepts[tweet.concepts[i]] == true) {

                return true;
            }
        }

        return false;


    };

    $scope.filterByEntity = function(tweet) {
        var i;
        if (!tweet.entities) {
            return true;
        }


        for (i in tweet.entities) {
            if ($scope.entities[tweet.entities[i]] == true)
                return true;
        }

        return false;


    };




    function translate() {
        var deferred = $q.defer();

        $http.get('http://159.203.101.53/ir/translate.php?text=' + encodeURIComponent($scope.search)).then(function(response) {
            $scope.boosts = {
                "en": "1",
                "de": "1",
                "ru": "1",
                "fr": "1",
                "ar": "1"
            }

            $scope.query_lang = response.data.lang;
            $scope.boosts[$scope.query_lang] = "3"

            $scope.query_en = response.data.en
            $scope.query_de = response.data.de
            $scope.query_ru = response.data.ru
            $scope.query_fr = response.data.fr
            $scope.query_ar = response.data.ar



            $log.info($scope.query_lang)
            deferred.resolve("Completed translation");
            $log.info("Completed translation");


        }, function(error) {
            deferred.reject("Translation failed");

        });

        return deferred.promise;


    }


    function fetch(id) {

        $scope.id_map = {
            "1": "text_en+text_de+text_ru+text_fr",
            "2": "tweet_hashtags",
            "3": "concepts",
            "4": "entities"
        }

        $scope.processing = true;
        $scope.languages = {};
        $scope.concepts = {};
        $scope.entities = {};
        $scope.summary = {};
        $scope.concepts_count = {};
        $scope.entities_count = {};
        $scope.languages_count = {};


        $log.info("Translating..");

        translate().then(function(resolved) {
            $scope.timer_start = new Date().getTime();

            $log.info("English -> " + $scope.query_en);
            $log.info("German -> " + $scope.query_de);
            $log.info("Russian -> " + $scope.query_ru);
            $log.info("French -> " + $scope.query_fr);
            $log.info("Arabic -> " + $scope.query_ar);

            if (id != 1) {
                $scope.full_q = '"' + $scope.query_en + '"'
                $scope.url = "http://52.26.115.208:8983/solr/irsearch/select?q=" + encodeURIComponent($scope.full_q) + "&rows=10000&wt=json&indent=true&defType=dismax&qf=" + $scope.id_map[id] + "&facet=true&facet.field=concepts&facet.field=lang&facet.field=entities"
            } else {
                $scope.query_en = "("+$scope.query_en+")" + "^" + $scope.boosts["en"];
                $scope.query_de = "("+$scope.query_de+")" + "^" + $scope.boosts["de"];
                $scope.query_ru = "("+$scope.query_ru+")" + "^" + $scope.boosts["ru"];
                $scope.query_fr = "("+$scope.query_fr+")" + "^" + $scope.boosts["fr"];
                $scope.query_ar = "("+$scope.query_ar+")" + "^" + $scope.boosts["ar"];

                $scope.full_q = "text_en:" + $scope.query_en + " OR " + "text_de:" + $scope.query_de + " OR " + "text_ru:" + $scope.query_ru + " OR " + "text_fr:" + $scope.query_fr
                $scope.url = "http://52.26.115.208:8983/solr/irsearch/select?q=" + encodeURIComponent($scope.full_q) + "&rows=10000&wt=json&indent=true&facet=true&facet.field=concepts&facet.field=lang&facet.field=entities"

            }



            $log.info('Fetching JSON from ' + $scope.url)

            $http.get($scope.url)
                .then(function(response) {
                    
                    $scope.concepts_dummy = (response.data.facet_counts.facet_fields.concepts)
                    $scope.entities_dummy = (response.data.facet_counts.facet_fields.entities)
                    $scope.lang_dummy = (response.data.facet_counts.facet_fields.lang)
                    for (i = 0; i <= $scope.concepts_dummy.length; i = i + 2) {
                        if ($scope.concepts_dummy[i + 1] > 0) {

                            $scope.concepts[$scope.concepts_dummy[i]] = true
                            $scope.concepts_count[$scope.concepts_dummy[i]] = $scope.concepts_dummy[i + 1]
                            if (i == 10)
                                break;
                        }

                    }
                    for (i = 0; i <= $scope.entities_dummy.length; i = i + 2) {
                        if ($scope.entities_dummy[i + 1] > 0) {

                            $scope.entities[$scope.entities_dummy[i]] = true
                            $scope.entities_count[$scope.entities_dummy[i]] = $scope.entities_dummy[i + 1]
                            if (i == 10)
                                break;
                        }

                    }
                    for (i = 0; i < $scope.lang_dummy.length; i = i + 2) {
                        if ($scope.lang_dummy[i + 1] > 0) {
                            $scope.languages[$scope.lang_dummy[i]] = true
                            $scope.languages_count[$scope.lang_dummy[i]] = $scope.lang_dummy[i + 1]
                            if (i == 10)
                                break;
                        }

                    }


                    response = response.data;
                    $log.info("Success");
                    $scope.b_tweets = response;


                    $scope.totalItems = response.response.numFound;
                    if($scope.totalItems==0)
                        $scope.show_top=true;
                    else
                        $scope.show_top = false;
                    $log.info("Number of documents found - " + response.response.numFound);
                    $scope.timer_end = new Date().getTime();
                    $scope.response_time = $scope.timer_end - $scope.timer_start;
                    // Populate filters
                    $scope.raw_tweets = $scope.b_tweets.response.docs
                    var i, j;
                    var flag = 0;

                    if (id == 3 || id == 4)

                        $scope.summary_topic = $scope.search
                    else
                        $scope.summary_topic = Object.keys($scope.entities)[0]


                    $log.info("Fetching summary for " + $scope.summary_topic + "...");







                    $http.get('http://159.203.101.53/ir/summary.php?titles=' + encodeURIComponent($scope.summary_topic)).then(function(response) {

                        $scope.summary['summary'] = response.data.summary;
                        $scope.summary['image'] = response.data.image;
                        $scope.tweets = $scope.b_tweets;
                        $scope.processing = false;



                    }, function(error) {
                        $log.info("Fetching summary for " + $scope.raw_tweets[0].entities[0] + "...failed");
                        $scope.tweets = $scope.b_tweets;
                        $scope.processing = false;


                    });








                    if (flag == 0) {
                        $scope.processing = false;

                        $scope.tweets = $scope.b_tweets;
                    }


                }, function(error) {
                    $log.info("Solr is not running");
                    $scope.error = "Solr is not running";
                    $scope.processing = false;

                });


        });

    }


    $scope.select = function() {
        this.setSelectionRange(0, this.value.length);
    }



    $scope.maxSize = 5;
    $scope.currentPage = 1;
    $scope.pageSize = 10;
});




app.controller('ModalCtrl', function($scope, $uibModal, $log, $http) {


    $scope.animationsEnabled = true;

    $scope.open = function(tweet) {



        var modalInstance = $uibModal.open({
            animation: $scope.animationsEnabled,
            templateUrl: 'expanded_tweet.html',
            controller: 'ModalInstanceCtrl',
            resolve: {
                expanded_tweet: function() {
                    return tweet;
                }
            }
        });

        modalInstance.result.then(function(selectedItem) {
            $log.info('Modal dismissed at: ' + new Date());
        }, function() {
            $log.info('Modal dismissed at: ' + new Date());
        });
    };

    $scope.toggleAnimation = function() {
        $scope.animationsEnabled = !$scope.animationsEnabled;
    };

});

// Please note that $modalInstance represents a modal window (instance) dependency.
// It is not the same as the $uibModal service used above.

app.controller('ModalInstanceCtrl', function($scope, $uibModalInstance, $log, $http, expanded_tweet) {
    $scope.expanded_tweet = expanded_tweet;

    $log.info(expanded_tweet.id)

    $http.get('http://52.26.115.208:8983/solr/irsearch/mlt?q=id:' + expanded_tweet.id + '&mlt.fl=concepts,entities,text_en,text_de,text_ru,text_fr&mlt.boost=true&mlt.qf=concepts^2+entities^2+text_en+text_de+text_ru+text_fr&mlt.mindf=1&mlt.mintf=1&rows=5&wt=json&indent=true').then(function(response) {
        $scope.related = response.data.response.docs





    }, function(error) {

    });


    $scope.ok = function() {
        $uibModalInstance.close();
    };

    $scope.cancel = function() {
        $uibModalInstance.dismiss();
    };
});



app.controller('AnalyticsController', function($scope, $log, $http, $route) {
    $log.info('Loaded analytics')
    $scope.show_graph = false;
    $scope.language_map = {
        "en": "English",
        "ru": "Russian",
        "de": "German",
        "fr": "French",
        "ar": "Arabic"
    }




    $http.get('http://52.26.115.208:8983/solr/irsearch/select?q=*%3A*&wt=json&indent=true&facet=true&facet.field=topic&facet.field=lang').then(function(response) {



        $scope.topics = response.data.facet_counts.facet_fields.topic
        $scope.languages = response.data.facet_counts.facet_fields.lang
        $scope.languages_chart = [];
        $scope.topics_chart = [];


        for (var i = 0; i < 6; i += 2) {
            $scope.topics_chart.push({
                label: $scope.topics[i],
                value: $scope.topics[i + 1]
            })

        }

        for (var i = 0; i < 8; i += 2) {

            $scope.languages_chart.push({
                label: $scope.language_map[$scope.languages[i]],
                value: $scope.languages[i + 1]
            })

        }

        $log.info($scope.languages_chart)
        $log.info($scope.topics_chart)


        $scope.LanguageData = {
            chart: {
                caption: "Languages",
                startingangle: "120",
                showlabels: "0",
                showlegend: "1",
                enablemultislicing: "0",
                slicingdistance: "30",
                showpercentvalues: "1",
                showpercentintooltip: "0",
                plottooltext: "Language : $label <br/> Number of tweets : $datavalue",
                theme: "fint",
                animation: true
            },
            data: $scope.languages_chart
        }

        $scope.TopicData = {
            chart: {
                caption: "Topics",
                startingangle: "120",
                showlabels: "0",
                showlegend: "1",
                enablemultislicing: "0",
                slicingdistance: "30",
                showpercentvalues: "1",
                showpercentintooltip: "0",
                plottooltext: "Topic : $label <br/> Number of tweets : $datavalue",
                theme: "fint",
                animation: true
            },
            data: $scope.topics_chart
        }




        $scope.show_graph = true;






    }, function(error) {

    });


    $http.get('http://52.26.115.208:8983/solr/irsearch/select?q=topic%3ASyrianCrisis&wt=json&indent=true&sort=retweet_count%20desc').then(function(response) {

        $scope.docs_sc = response.data.response.docs

    }, function(error) {

    });


    $http.get('http://52.26.115.208:8983/solr/irsearch/select?q=topic%3AParisAttacks&wt=json&indent=true&sort=retweet_count%20desc').then(function(response) {

        $scope.docs_pa = response.data.response.docs

    }, function(error) {

    });


    $http.get('http://52.26.115.208:8983/solr/irsearch/select?q=topic%3AKenyanBombing&wt=json&indent=true&sort=retweet_count%20desc').then(function(response) {

        $scope.docs_kb= response.data.response.docs

    }, function(error) {

    });




});


app.controller('MasterController', function($scope, $log, $route, $http) {
    $scope.$route = $route; /* To detect active tab */
    /* Fix for Fusion charts */
    eve.on('raphael.new', function() {
        this.raphael._url = this.raphael._g.win.location.href.replace(/#.*?$/, '');
    });
    /*End Fix*/






});
