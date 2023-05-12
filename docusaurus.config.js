const lightCodeTheme = require('prism-react-renderer/themes/vsDark');
const darkCodeTheme = require('prism-react-renderer/themes/dracula');

/** @type {import('@docusaurus/types').Config} */
const config = {
    title: 'Pywss',
    tagline: 'pywss docs',
    favicon: 'img/dd.ico',
    url: 'https://czasg.github.io',
    baseUrl: '/pywss',
    organizationName: 'czasg', // Usually your GitHub org/user name.
    projectName: 'pywss', // Usually your repo name.

    onBrokenLinks: 'throw',
    onBrokenMarkdownLinks: 'warn',
    i18n: {
        defaultLocale: 'en',
        locales: ['en'],
    },

    presets: [
        [
            'classic',
            /** @type {import('@docusaurus/preset-classic').Options} */
            ({
                docs: {
                    sidebarPath: require.resolve('./sidebars.js'),
                    routeBasePath: '/',
                    editUrl: 'https://github.com/czasg/pywss/edit/docs',
                },
                blog: false,
                theme: {
                    customCss: require.resolve('./src/css/custom.css'),
                },
            }),
        ],
    ],

    themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
        ({
            docs: {
                sidebar: {
                    hideable: false,
                    autoCollapseCategories: true,
                },
            },
            colorMode: {
                defaultMode: 'light',
                disableSwitch: false,
                respectPrefersColorScheme: false,
            },
            navbar: {
                title: 'Pywss 文档',
                logo: {
                    alt: 'cat',
                    src: 'img/dd.ico',
                    href: '/',
                },
                hideOnScroll: false,
                items: [
                    {
                        position: 'right',
                        type: 'html',
                        value: `<a class="header-github-link" target="_blank" href="https://github.com/czasg/pywss"/>`,
                    },
                ],
            },
            footer: {
                style: 'dark',
                links: [
                    {
                        title: 'Py开源项目',
                        items: [
                            {
                                label: 'Pywss',
                                href: 'https://github.com/czasg/pywss',
                            },
                            {
                                label: 'Loggus',
                                href: 'https://github.com/czasg/loggus',
                            },
                        ],
                    },
                    {
                        title: 'Go开源项目',
                        items: [
                            {
                                label: 'Go Queue',
                                href: 'https://github.com/czasg/go-queue',
                            },
                            {
                                label: 'Go Env',
                                href: 'https://github.com/czasg/go-env',
                            },
                            {
                                label: 'Go Set',
                                href: 'https://github.com/czasg/go-set',
                            },
                            {
                                label: 'Gonal',
                                href: 'https://github.com/czasg/gonal',
                            },
                            {
                                label: 'Snow',
                                href: 'https://github.com/czasg/snow',
                            },
                        ],
                    },
                    {
                        title: '活跃社区',
                        items: [
                            {
                                label: 'GitHub',
                                href: 'https://github.com/czasg',
                            },
                            {
                                label: 'V2EX',
                                href: 'https://www.v2ex.com',
                            },
                            {
                                label: 'Stack Overflow',
                                href: 'https://stackoverflow.com',
                            },
                        ],
                    },
                    {
                        title: '官方文档',
                        items: [
                            {
                                label: 'Py标准库',
                                href: 'https://docs.python.org/zh-cn/3/library/index.html',
                            },
                        ],
                    },
                ],
                copyright: `Copyright © ${new Date().getFullYear()} Czasg's Site.`,
            },
            prism: {
                theme: lightCodeTheme,
                darkTheme: darkCodeTheme,
            },
        }),
};

module.exports = config;
