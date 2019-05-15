import { Component, ElementRef, ViewChild } from '@angular/core';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { FormGroup, Validators, FormBuilder } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { DomSanitizer } from '@angular/platform-browser';

@Component({
  selector: 'app-main',
  templateUrl: './main.component.html',
  styleUrls: ['./main.component.css']
})
export class MainComponent {

  form: FormGroup;
  loading: boolean = false;
  imagePath: any;

  @ViewChild('fileInput') fileInput: ElementRef;
  
  isHandset$: Observable<boolean> = this.breakpointObserver.observe(Breakpoints.Handset)
    .pipe(
      map(result => result.matches)
    );

  constructor(private breakpointObserver: BreakpointObserver, 
    private fb: FormBuilder, 
    private http: HttpClient,
    private _sanitizer: DomSanitizer)
  {
    this.createForm();
  }

  createForm() {
    this.form = this.fb.group({
      
      diagram: null
    });
  }

  onFileChange(event) {
    let reader = new FileReader();
    if(event.target.files && event.target.files.length > 0) {
      let file = event.target.files[0];
      reader.readAsDataURL(file);
      reader.onload = () => {
        this.form.get('diagram').setValue({
          filename: file.name,
          filetype: file.type,
          value: (reader.result as string).split(',')[1]
        })
      };
    }
  }

  
  onSubmit() {
    const formModel = this.form.value;
    this.loading = true;

    this.http.post('http://localhost:5050/diagramDetection', formModel.diagram.value).subscribe((value: any) =>{
      this.imagePath = this._sanitizer.bypassSecurityTrustResourceUrl('data:image/jpg;base64,'   + value.image);
      this.loading = false;
    }, (error: any) => {
      alert('An error ocurred: '+error)
    })
    
  }
  
}
