import { Component } from '@angular/core';
import { OrganizationChartModule } from 'primeng/organizationchart';
import { DividerModule } from 'primeng/divider';
@Component({
  selector: 'app-about',
  standalone: true,
  imports: [OrganizationChartModule,DividerModule],
  templateUrl: './about.component.html',
  styleUrl: './about.component.scss'
})
export class AboutComponent {
  data: any[] = [
    {
      label: 'WD Web Solutions',
      expanded: true, // Set the root node to be expanded
      data: { image: 'assets/images/ShortSticker1.png' },
      children: [
        {
          label: 'Derek Dreibrodt',
          expanded: true, // Set each child node to be expanded
          data: { name: 'Derek Dreibrodt', title: 'Manager', image: 'assets/images/derekd.jpeg' },
          children: [
            {
              label: 'Co - Owner',
              data: {  }
            },
            {

              label: 'Lead Developer',
              data: {  }
            }
            
          ]
        },
        {
          label: 'Zachary Whittenton',
          expanded: true, // Set each child node to be expanded
          data: { name: 'Zachary Whittenton', title: 'Manager', image: 'assets/images/zachw.jpeg' },
          children: [
            {
              label: 'Co - Owner',
              data: {  }
            },
            {
              label: 'Senior Developer',
              data: {  }
            }
          ]
        }
      ]
    }
  ];

  selectedNodes: any[] = [];
}
