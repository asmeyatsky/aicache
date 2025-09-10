import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ICommandPalette } from '@jupyterlab/apputils';

import { IMainMenu } from '@jupyterlab/mainmenu';

import { ISettingRegistry } from '@jupyterlab/settingregistry';

import { IStatusBar } from '@jupyterlab/statusbar';

import { INotebookTracker } from '@jupyterlab/notebook';

import '../style/index.css';

/**
 * Initialization data for the aicache-jupyterlab extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: '@aicache/jupyterlab-extension:plugin',
  autoStart: true,
  requires: [
    ICommandPalette,
    IMainMenu,
    ISettingRegistry,
    IStatusBar,
    INotebookTracker
  ],
  activate: (
    app: JupyterFrontEnd,
    palette: ICommandPalette,
    mainMenu: IMainMenu,
    settingRegistry: ISettingRegistry,
    statusBar: IStatusBar,
    notebookTracker: INotebookTracker
  ) => {
    console.log('JupyterLab extension aicache-jupyterlab is activated!');

    // TODO: Initialize aicache service
    // const aicacheService = new AicacheService();

    // TODO: Register commands
    // const commands = new AicacheCommands(
    //   app,
    //   palette,
    //   mainMenu,
    //   aicacheService
    // );

    // TODO: Add sidebar
    // const sidebar = new AicacheSidebar(aicacheService);
    // app.shell.add(sidebar, 'left', { rank: 200 });

    // Handle settings
    Promise.all([settingRegistry.load(plugin.id), app.restored])
      .then(([settings]) => {
        console.log('aicache settings loaded:', settings.composite);
      })
      .catch(reason => {
        console.error('Failed to load settings for aicache-jupyterlab.', reason);
      });
  }
};

export default plugin;