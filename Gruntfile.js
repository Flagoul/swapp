module.exports = function(grunt) {
    grunt.initConfig({
        copy: {
            main: {
                files: [
                    {
                        expand: true,
                        src: ['node_modules/font-awesome/fonts/*'],
                        dest: 'static/public/fonts/',
                        flatten: true
                    }, {
                        expand: true,
                        src: [
                            'node_modules/tether/dist/js/tether.js',
                            'node_modules/imagesloaded/imagesloaded.pkgd.js',
                            'node_modules/jquery/dist/jquery.js',
                            'node_modules/bootstrap/dist/js/bootstrap.js',
                            'node_modules/isotope-layout/dist/isotope.pkgd.js',
                            'node_modules/flickity/dist/flickity.pkgd.js',
                            'node_modules/jquery-match-height/dist/jquery.matchHeight.js',
                            'node_modules/zone.js/dist/zone.js',
                            'node_modules/reflect-metadata/Reflect.js',
                            'node_modules/systemjs/dist/system.src.js'
                        ],
                        dest: 'static/public/js/vendor/',
                        flatten: true
                    }, {
                        expand: true,
                        cwd: 'node_modules/@angular/',
                        src: ['**'],
                        dest: 'static/public/js/vendor/@angular/'
                    }, {
                        expand: true,
                        cwd: 'node_modules/rxjs/',
                        src: ['**'],
                        dest: 'static/public/js/vendor/rxjs/'
                    }
                ]
            }
        },
        sass: {
            dist: {
                files: {
                    'static/public/css/styles.css': 'static/scss/styles.scss'
                }
            }
        },
        ts: {
            default: {
                src: ["static/ts/**/*.ts", "!node_modules/**"],
                outDir: 'static/public/js/',
                options: {
                    "target": "es5",
                    "module": "commonjs",
                    "moduleResolution": "node",
                    "sourceMap": true,
                    "emitDecoratorMetadata": true,
                    "experimentalDecorators": true,
                    "removeComments": false,
                    "noImplicitAny": false
                }
            }
        },
        watch: {
            styles: {
                expand: true,
                files: ['**/*.scss'],
                tasks: ['sass']
            },
            livereload: {
                files : [
                    '**/static/public/js/*.js',
                    '**/templates/**/*.html',
                    '**/static/public/css/*.css',
                    '**/static/scss/*.scss',
                    '**/*.py'
                ],
                options: {
                    livereload: 8080
                }
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-contrib-sass');
    grunt.loadNpmTasks("grunt-ts");
    grunt.loadNpmTasks('grunt-contrib-watch');

    // Default task(s).
    grunt.registerTask('default', ['copy', 'sass', 'ts']);
};