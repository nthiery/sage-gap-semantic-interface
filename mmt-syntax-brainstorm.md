sage = http://www.sagemath.org?
gap = http://www.gap-system.org?
mmt = http://latin.omdoc.org/math?


sage:Magmas    =>  mmt:Magma
     _mul_  =>  ∘
     *  is an alias for _mul_ 

sage:Magmas.Commutative => mmt:Commutative
  ??? => commut
  
sage:Semigroups => Semigroup
  ??? => assoc

sage:Monoids => mmt:Monoid

sage:Monoids.Commutative => mmt:CommutativeMonoid
      free (returns the free monoid) => ???

sage:Groups => mmt:Group

sage:Magmas.Unital.Inverse => mmt:Inverse
       __invert__ =>  inv

In Sage/Python syntax:
=================
    
(Magma,"additive")
(Semigroup, "additive")


@mmt("Magma","additive", file="additive_magmas.py")
class AdditiveMagmas:

       class ElementMethods:

            @mmt("∘", operator="+")
            @abstract_method
            def _add_(self, other):
                 pass

      @mmt.NeutralElement
      class AdditiveUnital:
            class ParentMethods:
                  @mmt("neutral")
                  @abstract_method:
                  def zero(self):
                        pass

                             # Generates automatically in the XXX.GAP category

                             def zero(self): return self(self.gap().Zero())


       @mmt.method(inner=True, gap="Subtract")

       @abstract_method

       def _sub_(self, other):

            pass


          # Generates automatically

          def _sub_(self,other): return self(gap.Subtract(self.gap(), other.gap()))


@mmt("Semigroups")
class AdditiveSemigroups:
      class P

@mmt("Ring")
class Rings:
        def super_categories(self):
             return [Magmas(), AdditiveMagmas()]

        

dans mmt.py:
    
    from sage.categories ... import AdditiveSemigroups
    from sage.categories
    
    mmt("Semigroups")(AdditiveSemigroups)
    mmt("NeutralElement")(AdditiveMagmas.AdditiveUnital)
    mmt("neutral")(AdditiveMagmas.AdditiveUnital.ParentMethods.zero)
    
    


// Different realms (-> in MMT):   math definitions (-> theory), data structures (->codecs), algorithms (-> implements)


Magma-based theories in MMT/LF/FOL
https://gl.mathhub.info/MMT/LATIN/blob/master/source/math/magmas.elf

http://latin.omdoc.org/math?Magma?

%view OppositeMagma : Magma -> Magma = {
  ∘ := [x][y] y ∘ x.
}.

%sig Commutative = {
  %meta EqUniverse.
  %include Magma. 
  commut : X ∘ Y == Y ∘ X.
}.

%view OppositeCommutative : Commutative -> Commutative = {
  %include OppositeMagma.
  commut := [X][Y] commut.
}.

%sig Semigroup = {
  %meta EqUniverse.
  %include Magma.
  assoc : (X ∘ Y) ∘ Z == X ∘ (Y ∘ Z).
  ab∘cd==a∘bc∘d : (A ∘ B) ∘ (C ∘ D) == (A ∘ (B ∘ C)) ∘ D
     = trans3 assoc (applyL A (sym assoc)) (sym assoc).
}.

%view OppositeSemigroup : Semigroup -> Semigroup = {
  %include OppositeMagma.
  assoc := [X][Y][Z] sym assoc.
}.

%sig CommutativeSemigroup = {
  %meta EqUniverse.
  %include Semigroup.
  %include Commutative.
  ab∘cd==ac∘bd : (A ∘ B) ∘ (C ∘ D) == (A ∘ C) ∘ (B ∘ D)
     = trans3 ab∘cd==a∘bc∘d (applyR D (applyL A commut)) (sym ab∘cd==a∘bc∘d).
}.

%view OppositeCommutativeSemigroup : CommutativeSemigroup -> CommutativeSemigroup = {
  %include OppositeSemigroup.
  %include OppositeCommutative.
}.

%sig Idempotent = {
  %meta EqUniverse.
  %include Magma. 
  idem : X ∘ X == X.
}.

%sig Band = {
  %meta EqUniverse.
  %include Semigroup.
  %include Idempotent.
}.

%sig CancellationLeft = {
   %meta EqUniverse.
   %include Magma.
   cancel : X ∘ Y == X ∘ Y' -> Y == Y'.
}.

%% %sig CancellationRight = OppositeMagma(CancellationLeft).
%sig CancellationRight = {
   %meta EqUniverse.
   %include Magma.
   cancel : X ∘ Y == X' ∘ Y -> X == X'.
}.

%sig PointedMagma = {
   %meta EqUniverse.
   %include Magma.
   point : u.
}.
%view OppositePointedMagma : PointedMagma -> PointedMagma = {
   %include OppositeMagma.
   point := point.
}.

%sig NeutralElementRight = {
  %meta EqUniverse.
  %include PointedMagma %open point %as e. 
  neutral : X ∘ e == X.
}.

%% %sig NeutralElementLeft = OppositeMagma(NeutralElementRight)
%sig NeutralElementLeft = {
  %meta EqUniverse.
  %include PointedMagma %open point %as e.
  neutral : e ∘ X == X.
}.

%sig NeutralElement = {
  %meta EqUniverse.
  %include NeutralElementRight %open neutral %as idenR.
  %include NeutralElementLeft %open neutral %as idenL.
}.

%{
%view NeutralCommute : NeutralElement -> NeutralElementRight Commutative = {
}.
}%


%view NELNE : NeutralElementLeft -> NeutralElement = {
        %include OppositePointedMagma.
        neutral := [x] idenR.
}.

%view NERNE : NeutralElementRight -> NeutralElement = {
        %include OppositePointedMagma.
        neutral := [x] idenL.
}.


%view OppositeNeutralElement : NeutralElement -> NeutralElement = {
        %include NELNE.
        %include NERNE.
}.


%sig Monoid = {
  %meta EqUniverse.
  %include Semigroup.
  %include NeutralElement.
}.

%sig CommutativeMonoid = {
  %meta EqUniverse.
  %include Monoid.
  %include Commutative.
}.

%sig Inverse = {
  %meta EqUniverse.
  %include NeutralElement.
    inv : u -> u.
}.

%sig RightInverse = {
  %meta EqUniverse.
  %include Inverse.
  inverse : X ∘ (inv X) == e.
}.

%{
%view CRRI : CancellationRight -> RightInverse + Semigroup = {
        cancel := [x][y][x'][p]  trans4 (trans4  (sym idenR)  (cong ([t] x ∘ t) (sym inverse)) (sym assoc) (cong ([t] t ∘ (inv y)) p)) (assoc) (cong ([t] x' ∘ t) inverse) idenR.
}.
}%

%% %sig LeftInverse = OppositeNeutralElement(RightInverse)
%sig LeftInverse = {
  %meta EqUniverse.
  %include Inverse.
  inverse : (inv X) ∘ X == e.
}. 

%sig Group = {
  %meta EqUniverse.
  %include Monoid.
  %include RightInverse %open inverse %as inv_right.
  
  inv_left : (inv X) ∘ X == e = trans  (cong ([t] (inv X) ∘ t) (trans (trans4 
                                                  (sym idenR)
                                                  (cong ([t] X ∘ t) (sym inv_right))
                                                  (sym assoc)
                                                  (cong ([t]  t ∘ (inv (inv X))) (inv_right)))
                                                  (idenL)))  (inv_right).
  
  inv_invE : inv (inv X) == X = trans (trans4 
                                                                        (sym idenL) 
                                                                        (cong ([t] (t ∘ inv (inv X))) (sym inv_right)) 
                                                                        (assoc) 
                                                       (cong ([t] X ∘ t) (inv_right))) 
                                                       (idenR).
  inv_distr : inv (X ∘ Y) == (inv Y) ∘ (inv X) = sym (trans (trans4 (sym idenR) (cong ([t] ((inv Y) ∘ (inv X)) ∘ t) (sym inv_right)) (sym assoc) (cong ([t] t ∘ inv (X ∘ Y)) (ab∘cd==a∘bc∘d)))
                                                                             (trans4  (cong ([t] (((inv Y) ∘ t) ∘ Y) ∘ inv (X ∘ Y)) (inv_left)) 
                                                                                          (cong ([t] (t ∘ Y) ∘ inv (X ∘ Y)) (idenR)) 
                                                                                          (cong ([t] t ∘ inv (X ∘ Y)) (inv_left))  
                                                                                          (idenL))).
}.

%view LIG : LeftInverse -> Group = {
        inverse := [x] inv_left.
}.

%sig AbelianGroup = {
  %meta EqUniverse.
  %include Group  %open ∘ %as + e %as 0 inv %as -.
  %include Commutative.
}.

%sig Division = {
   %meta EqUniverse.
   %include PointedMagma %open ∘ %as / point %as e.
   cancel_denom : (X / Z) / (Y / Z) == X / Y.
   identity : X / X == e.
   double_inversion : e / (e / X) == X.
   
   neutrality : X / e == X = trans3 (sym cancel_denom) (cong ([t] t / (e / X)) identity) (double_inversion).
}.

%sig AbelianDivision = {
   %meta EqUniverse.
   %include Division.
   cancel_enum : (Z / X) / (Z / Y) == Y / X.
}.

%view  MD : Magma -> Division = {
        ∘ := [x][y] x / (e / y).
}.


%view SD : Semigroup -> Division = {
  %include MD.
  assoc :=  [x][y][z] sym (trans4
  (cong ([t] x / (t / (y / (e / z)))) (sym identity))
  (cong ([t] x / t) (cancel_denom))
  (cong ([t] t / ((e / z) / y)) (trans3 (sym neutrality) (sym cancel_denom) (cong ([t] (x / (e / y)) / t) double_inversion)))
  (cong ([t] t) (cancel_denom))).
}.

%view NER : NeutralElementRight -> Division = {
        %include MD.
        neutral := [x] trans (cong ([t] x / t) (identity)) neutrality.
}.

%view NEL : NeutralElementLeft -> Division = {
        %include MD.
        neutral := [x] double_inversion.
}.

%view NE : NeutralElement -> Division = {
        %include NER.
        %include NEL.
        
}.

%view MND : Monoid -> Division = {
  %include SD.
  %include NE.  
}.

%view ID : Inverse -> Division = {
  %include NE.
  inv := [x] e / x.
}.

%view LI : LeftInverse -> Division = {
  %include ID.
  inverse := [x] identity.
}.

%view RI : RightInverse -> Division = {
  %include ID.        
  inverse := [x] trans (cong ([t] x / t) (double_inversion)) identity.
}.

%view GD : Group -> Division = {
  %include MND.
  %include RI.
  
 }.

%view CD : Commutative  -> AbelianDivision = {
        %include MD.
  commut := [x][y] trans (cong ([t] t / (e / y)) (sym double_inversion)) cancel_enum.        
}.
 
%view GCD : AbelianGroup -> AbelianDivision = {
         %include GD.
         %include CD.
 }.
 
%view MG : Magma -> Group = {
        ∘ := [x][y] x ∘ (inv y). 
}.
 
%view DG : Division -> Group = {
        %include MG.
   cancel_denom         := [x][z][y] trans4 
                                                           (cong ([t] (x ∘ (inv z)) ∘ t ) inv_distr)
                                                           (ab∘cd==a∘bc∘d)
                                                           (cong ([t] (x ∘ t) ∘ (inv y))  inv_right)
                                                           (cong ([t] t ∘ (inv y))    idenR).
   identity := [X] inv_right.
   double_inversion := [X] trans3
                                                   (idenL)
                                                   (cong ([t] inv t) idenL)
                                                   (inv_invE).
}.

%view DCG : AbelianDivision -> AbelianGroup = {
        %include DG.
        cancel_enum := [z][x][y] trans3 (trans4 (commut) (cong ([t] t ∘ (z ∘ (inv x))) inv_distr) (ab∘cd==a∘bc∘d) (cong ([t] ((inv (inv y)) ∘ t) ∘ (inv x) ) (inv_left))) 
                                                          (cong ([t] t ∘ (inv x)) idenR) (cong ([t] t ∘ (inv x)) inv_invE).
}.
